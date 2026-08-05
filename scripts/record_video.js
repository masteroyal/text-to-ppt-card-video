#!/usr/bin/env node
/**
 * record_video.js — Screenshot-based per-page HTML recording.
 *
 * Uses tab.screenshot() polling instead of CDP screencast to avoid
 * encoder backlog (6-8s frame delay). Elements are triggered from
 * audio.currentTime with ELEMENT_LEAD=0.5s before audio segments.
 *
 * Usage:
 *   node record_video.js <pages_dir> <output.mp4> [width] [height]
 *
 * Expects: pages_dir/page_0.html, page_1.html, ..., page_N.html
 *
 * Requirements:
 *   npm install puppeteer
 *   ffmpeg on PATH
 */

const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { spawnSync } = require('child_process');

// Add local node_modules to module resolution path
const localNodeModules = path.join(__dirname, 'node_modules');
if (fs.existsSync(localNodeModules)) {
  module.paths.unshift(localNodeModules);
}

// Also try the calling project's node_modules
const cwdNodeModules = path.join(process.cwd(), 'node_modules');
if (fs.existsSync(cwdNodeModules)) {
  module.paths.unshift(cwdNodeModules);
}

const puppeteer = require('puppeteer');

function sleep(ms) {
  return new Promise(function(resolve) { setTimeout(resolve, ms); });
}

function pad6(n) {
  return n.toString().padStart(6, '0');
}

// Pages without narration still need a visible duration in the final video.
var MIN_PAGE_SECONDS = 2.0;

function runFfmpeg(args) {
  var result = spawnSync('ffmpeg', args, { stdio: 'pipe', encoding: 'utf-8' });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    var stderr = (result.stderr || '').slice(-800);
    throw new Error('ffmpeg failed (exit ' + result.status + '): ' + stderr);
  }
  return result;
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.log('Usage: node record_video.js <pages_dir> <output.mp4> [width] [height]');
    process.exit(1);
  }

  const pagesDir = path.resolve(args[0]);
  const outputPath = path.resolve(args[1]);
  const width = parseInt(args[2]) || 1080;
  const height = parseInt(args[3]) || 1920;

  // Find per-page HTML files
  var pageFiles = [];
  for (var i = 0; ; i++) {
    var fp = path.join(pagesDir, 'page_' + i + '.html');
    if (!fs.existsSync(fp)) break;
    pageFiles.push(fp);
  }

  if (pageFiles.length === 0) {
    console.error('ERROR: No page_*.html files found in ' + pagesDir);
    process.exit(1);
  }

  console.log('[text-to-ppt-card-video] Recording video (screenshot-based)...');
  console.log('  Pages dir: ' + pagesDir);
  console.log('  Output: ' + outputPath);
  console.log('  Pages: ' + pageFiles.length);
  console.log('  Resolution: ' + width + 'x' + height);

  const tempDir = path.join(path.dirname(outputPath), '.video_temp');
  fs.mkdirSync(tempDir, { recursive: true });

  let browser = null;
  try {
    // Launch browser once (autoplay budget resets per new tab)
    console.log('[text-to-ppt-card-video] Launching browser...');
    browser = await puppeteer.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-features=IsolateOrigins,site-per-process',
        '--autoplay-policy=no-user-gesture-required'
      ]
    });

    var pageVideos = [];
    var pageDurations = [];

    for (var pageIdx = 0; pageIdx < pageFiles.length; pageIdx++) {
      var htmlPath = pageFiles[pageIdx];
      console.log('\n--- Page ' + (pageIdx + 1) + '/' + pageFiles.length + ' ---');

      // Open a new tab for this page (resets Chrome autoplay budget)
      var tab = await browser.newPage();
      await tab.setViewport({ width: width, height: height });

      await tab.goto(pathToFileURL(htmlPath).href, { waitUntil: 'networkidle0' });

      // Wait for audio to be ready (pages without narration have no audio src)
      await tab.waitForFunction(function() {
        var audio = document.querySelector('audio');
        if (!audio) return true;
        if (!audio.src || audio.src.indexOf('data:audio/mp3;base64,') === -1) return true;
        return audio.readyState >= 3;
      }, { timeout: 15000 });

      // Get page duration from TIMELINE
      var pageDur = await tab.evaluate(function() {
        if (typeof TIMELINE !== 'undefined' && TIMELINE.pages && TIMELINE.pages.length > 0) {
          return TIMELINE.pages[0].duration;
        }
        return 0;
      });
      if (!(pageDur > 0)) {
        pageDur = MIN_PAGE_SECONDS;
        console.log('  No narration; recording static page for ' + pageDur.toFixed(1) + 's');
      }
      pageDurations.push(pageDur);
      console.log('  Duration: ' + pageDur.toFixed(1) + 's');

      // Hide UI controls (not part of card content)
      await tab.evaluate(function() {
        var s = document.createElement('style');
        s.textContent = '.controls,.dots{display:none!important}';
        document.head.appendChild(s);
      });

      // Get card crop rectangle
      var cropRect = await tab.evaluate(function() {
        var card = document.querySelector('.card');
        if (!card) return null;
        var rect = card.getBoundingClientRect();
        return {
          x: Math.round(rect.x),
          y: Math.round(rect.y),
          width: Math.round(rect.width),
          height: Math.round(rect.height)
        };
      });

      if (!cropRect) {
        throw new Error('No .card found on page ' + (pageIdx + 1));
      }
      console.log('  Crop: (' + cropRect.x + ',' + cropRect.y + ') ' + cropRect.width + 'x' + cropRect.height);

      // ── Screenshot-based recording ──

      // ELEMENT_LEAD: trigger elements this many seconds before their audio segment.
      // 0.5s gives the 0.75s CSS opacity transition time to start fading in
      // just before the corresponding narration begins.
      var ELEMENT_LEAD = 0.5;

      // Fixed target FPS for capture and encoding. Using a constant ensures
      // frame intervals are uniform and video duration matches audio exactly.
      var TARGET_FPS = 8;
      var FRAME_INTERVAL = 1000 / TARGET_FPS; // ms per frame

      // Prepare page: hide elements, reset state, collect segments
      var pageSegments = await tab.evaluate(function() {
        var lf = window.__lf || {};
        if (lf.stop) lf.stop();
        if (lf.triggered) {
          for (var k in lf.triggered) { lf.triggered[k] = {}; }
        }
        var animSels = '.cover > *, .body > .breadcrumb, .body > h2, .body > .rule, .body > .exec, .body > p, .body > ul, .body > .table, .body > blockquote, .body > .source, .body > .metrics, .body > .grid, #cover-label, #cover-title, #cover-subtitle, #cover-tags, #cover-footer';
        document.querySelectorAll(animSels).forEach(function(el) {
          el.classList.remove('visible');
          el.style.opacity = '0';
        });
        var audio = document.querySelector('audio');
        if (audio) { audio.pause(); audio.currentTime = 0; }
        var pd = TIMELINE && TIMELINE.pages ? TIMELINE.pages[0] : null;
        if (lf.triggered && pd) {
          if (!lf.triggered[0]) lf.triggered[0] = {};
          pd.segments.forEach(function(seg, si) { lf.triggered[0][si] = true; });
        }
        return pd ? pd.segments : [];
      });

      // Pages without narration have no segments to trigger, so show the
      // whole card instead of leaving it blank during the static recording.
      if (pageSegments.length === 0) {
        await tab.evaluate(function() {
          var s = document.createElement('style');
          s.textContent = '.visible li,.visible .row{animation:none!important;opacity:1!important}';
          document.head.appendChild(s);
          var animSels = '.cover > *, .body > .breadcrumb, .body > h2, .body > .rule, .body > .exec, .body > p, .body > ul, .body > .table, .body > blockquote, .body > .source, .body > .metrics, .body > .grid, #cover-label, #cover-title, #cover-subtitle, #cover-tags, #cover-footer';
          document.querySelectorAll(animSels).forEach(function(el) {
            el.classList.add('visible');
            el.style.opacity = '';
          });
        });
      }

      // Start audio playback
      await tab.evaluate(function() {
        var audio = document.querySelector('audio');
        if (audio) audio.play().catch(function(e) { console.log('Play error:', e.message); });
      });

      // ── Screenshot capture loop ──
      console.log('  Recording ' + pageDur.toFixed(1) + 's via screenshots at ' + TARGET_FPS + 'fps...');
      var t0 = Date.now();
      var triggeredSet = {};
      var audioOk = false;
      var frameCount = 0;
      var screenshotDir = path.join(tempDir, 'screenshots_' + pageIdx);
      fs.mkdirSync(screenshotDir, { recursive: true });

      while (true) {
        var elapsed = (Date.now() - t0) / 1000;
        if (elapsed >= pageDur) break;

        // First: recover audio if paused + read actual audio time.
        // Using audio.currentTime (not wall-clock) ensures elements sync
        // to actual audio playback, compensating for play() latency and drift.
        var audioInfo = await tab.evaluate(function(elapsedSec) {
          var audio = document.querySelector('audio');
          if (!audio) return { time: elapsedSec, paused: true };
          if (audio.paused) {
            audio.currentTime = Math.min(elapsedSec, audio.duration || elapsedSec);
            audio.play().catch(function() {});
          }
          return { time: audio.currentTime, paused: audio.paused };
        }, elapsed);

        var audioTime = audioInfo.time;

        // Determine which elements to trigger based on AUDIO time
        var toTrigger = [];
        pageSegments.forEach(function(seg, si) {
          if (!triggeredSet[si] && audioTime >= (seg.start - ELEMENT_LEAD)) {
            triggeredSet[si] = true;
            seg.elements.forEach(function(eid) { toTrigger.push(eid); });
          }
        });

        if (toTrigger.length > 0) {
          console.log('  t=' + audioTime.toFixed(2) + 's (audio): triggering [' + toTrigger.join(',') + ']');
        }

        // Trigger elements in browser
        if (toTrigger.length > 0) {
          await tab.evaluate(function(ids) {
            var triggerEl = window.__lf.triggerEl;
            ids.forEach(function(id) {
              var el = document.getElementById(id);
              if (el && triggerEl) triggerEl(id);
            });
          }, toTrigger);
        }

        if (!audioOk && !audioInfo.paused && audioTime > 0.1) {
          audioOk = true;
          console.log('  Audio playing: ct=' + audioTime.toFixed(2) + 's');
        }

        // Adaptive sleep: maintain uniform TARGET_FPS frame intervals
        var framePath = path.join(screenshotDir, 'frame_' + pad6(frameCount) + '.jpg');
        await tab.screenshot({
          path: framePath,
          type: 'jpeg',
          quality: 85,
          clip: cropRect
        });
        frameCount++;

        // Log progress every 20 frames
        if (frameCount % 20 === 0) {
          console.log('    ' + frameCount + ' screenshots at t=' + elapsed.toFixed(1) + 's');
        }

        // Sleep until next frame's scheduled time
        var nextFrameTime = t0 + frameCount * FRAME_INTERVAL;
        var sleepMs = Math.max(0, nextFrameTime - Date.now());
        if (sleepMs > 0) await sleep(sleepMs);
      }

      console.log('  Recording done: ' + frameCount + ' screenshots in ' + ((Date.now() - t0) / 1000).toFixed(1) + 's');

      console.log('  Screenshots: ' + frameCount);

      // Close tab (frees memory, next page gets fresh tab)
      await tab.close();

      if (frameCount === 0) {
        throw new Error('No screenshots captured for page ' + (pageIdx + 1));
      }

      // Use TARGET_FPS for encoding — frames were captured at this uniform rate
      console.log('  Encoding at ' + TARGET_FPS + ' fps (' + frameCount + ' frames = ' + (frameCount / TARGET_FPS).toFixed(1) + 's)');

      // Encode page video from screenshots (already cropped to card region)
      var pageMp4 = path.join(tempDir, 'page_' + pageIdx + '.mp4');
      runFfmpeg([
        '-y',
        '-framerate', String(TARGET_FPS),
        '-i', path.join(screenshotDir, 'frame_%06d.jpg'),
        '-vf', 'scale=' + width + ':' + height + ':force_original_aspect_ratio=decrease:flags=lanczos,pad=' + width + ':' + height + ':(ow-iw)/2:(oh-ih)/2:color=black',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        pageMp4
      ]);
      pageVideos.push(pageMp4);
      console.log('  Page video: ' + (fs.statSync(pageMp4).size / 1024).toFixed(0) + ' KB');
    }

    await browser.close();
    browser = null;
    console.log('\n[text-to-ppt-card-video] Browser closed.');

    if (pageVideos.length === 0) {
      throw new Error('No page videos generated');
    }

    // ── Combine audio from all page HTMLs ──
    console.log('[text-to-ppt-card-video] Preparing combined audio...');
    var audioPath = extractCombinedAudio(pageFiles, tempDir, pageDurations);

    // ── Concatenate page videos ──
    console.log('[text-to-ppt-card-video] Concatenating ' + pageVideos.length + ' page videos...');
    var concatList = path.join(tempDir, 'video_concat.txt');
    var concatContent = pageVideos.map(function(p) {
      return "file '" + p.replace(/\\/g, '/') + "'";
    }).join('\n');
    fs.writeFileSync(concatList, concatContent);

    // Concat video streams (copy, no re-encode)
    var tempVideo = path.join(tempDir, 'video_only.mp4');
    runFfmpeg(['-y', '-f', 'concat', '-safe', '0', '-i', concatList, '-c', 'copy', tempVideo]);

    // Calculate total duration from page durations for precise trim
    var totalDuration = pageDurations.reduce(function(s, d) { return s + d; }, 0);

    // Mux video + audio (re-encode video for precise duration matching)
    runFfmpeg([
      '-y',
      '-i', tempVideo,
      '-i', audioPath,
      '-t', totalDuration.toFixed(2),
      '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
      '-c:a', 'aac',
      '-b:a', '192k',
      '-pix_fmt', 'yuv420p',
      outputPath
    ]);

    console.log('[text-to-ppt-card-video] Video saved: ' + outputPath);
    var fileSize = (fs.statSync(outputPath).size / 1024 / 1024).toFixed(1);
    var totalDur = pageDurations.reduce(function(s, d) { return s + d; }, 0);
    console.log('  File size: ' + fileSize + ' MB');
    console.log('  Total duration: ' + totalDur.toFixed(1) + 's');

  } finally {
    if (browser) {
      try { await browser.close(); } catch (err) {
        console.error('Browser close error:', err.message);
      }
    }
    fs.rmSync(tempDir, { recursive: true, force: true });
    console.log('[text-to-ppt-card-video] Temp files cleaned up.');
  }
}

/**
 * Extract audio from each page's HTML AUDIO_SRC and concatenate with FFmpeg.
 * Only parses after the AUDIO_SRC keyword to avoid duplicate matches from
 * TIMELINE.audio_base64 which contains the same data.
 */
function extractCombinedAudio(pageFiles, tempDir, pageDurations) {
  var audioFiles = [];
  pageFiles.forEach(function(htmlPath, idx) {
    var html = fs.readFileSync(htmlPath, 'utf-8');
    // Only search after AUDIO_SRC keyword to avoid double-matching TIMELINE.audio_base64
    var srcIdx = html.indexOf('AUDIO_SRC');
    var fp = path.join(tempDir, 'audio_' + idx + '.mp3');
    if (srcIdx !== -1) {
      var after = html.substring(srcIdx);
      var m = /data:audio\/mp3;base64,([A-Za-z0-9+/=]+)/.exec(after);
      if (m) {
        var data = Buffer.from(m[1], 'base64');
        fs.writeFileSync(fp, data);
        audioFiles.push(fp);
        return;
      }
    }
    // Page has no embedded audio (e.g. no narration): keep audio/video lengths aligned.
    var duration = pageDurations[idx] > 0 ? pageDurations[idx] : MIN_PAGE_SECONDS;
    console.log('  Page ' + idx + ' has no embedded audio; adding ' + duration.toFixed(1) + 's silence');
    runFfmpeg([
      '-y', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono',
      '-t', duration.toFixed(2),
      '-ar', '24000', '-ac', '1',
      '-c:a', 'libmp3lame', '-b:a', '192k',
      fp
    ]);
    audioFiles.push(fp);
  });

  if (audioFiles.length === 0) throw new Error('No audio found in page HTMLs');
  if (audioFiles.length === 1) return audioFiles[0];

  var concatList = path.join(tempDir, 'audio_concat.txt');
  fs.writeFileSync(concatList, audioFiles.map(function(p) {
    return "file '" + p.replace(/\\/g, '/') + "'";
  }).join('\n'));

  var combined = path.join(tempDir, 'audio_combined.mp3');
  runFfmpeg(['-y', '-f', 'concat', '-safe', '0', '-i', concatList, '-c:a', 'libmp3lame', '-b:a', '192k', combined]);
  return combined;
}

main().catch(function(err) {
  console.error('ERROR:', err.message);
  console.error(err.stack);
  process.exit(1);
});
