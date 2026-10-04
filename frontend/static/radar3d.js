/**
 * ==============================================================================
 * WATERMARK: Rajpal Singh Tanwar
 * Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
 * Job Radar & Recruiter Radar — 3D Animation & Visual Telemetry Engine
 * ==============================================================================
 */

(function () {
  'use strict';

  // --- 1. 3D GYROSCOPIC CARD TILT & SPECULAR GLARE ---
  function init3DCardTilt() {
    const selector = '.card, .recruiter-card, .stat-card, .metric-card, .radar-hud-card, .portal-card, [data-tilt-3d]';
    
    function attachTilt(el) {
      if (el._tiltInitialized) return;
      el._tiltInitialized = true;

      // Create dynamic glare overlay
      let glare = el.querySelector('.glare-3d-overlay');
      if (!glare) {
        glare = document.createElement('div');
        glare.className = 'glare-3d-overlay';
        el.appendChild(glare);
      }

      el.style.transformStyle = 'preserve-3d';
      el.style.willChange = 'transform';

      let bounds = null;
      let rafId = null;

      el.addEventListener('mouseenter', () => {
        bounds = el.getBoundingClientRect();
        el.style.transition = 'transform 0.12s ease-out, box-shadow 0.25s ease-out';
      });

      el.addEventListener('mousemove', (e) => {
        if (!bounds) bounds = el.getBoundingClientRect();
        const mouseX = e.clientX - bounds.left;
        const mouseY = e.clientY - bounds.top;

        const xPct = mouseX / bounds.width;
        const yPct = mouseY / bounds.height;

        // Max rotation +/- 15 degrees
        const rotX = ((0.5 - yPct) * 18).toFixed(2);
        const rotY = ((xPct - 0.5) * 18).toFixed(2);

        if (rafId) cancelAnimationFrame(rafId);
        rafId = requestAnimationFrame(() => {
          el.style.transform = `perspective(1000px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateZ(10px) scale3d(1.02, 1.02, 1.02)`;
          
          // Move specular glare reflection
          if (glare) {
            glare.style.opacity = '1';
            glare.style.background = `radial-gradient(circle at ${xPct * 100}% ${yPct * 100}%, rgba(255,255,255,0.22) 0%, rgba(255,255,255,0.02) 60%, transparent 80%)`;
          }
        });
      });

      el.addEventListener('mouseleave', () => {
        if (rafId) cancelAnimationFrame(rafId);
        el.style.transition = 'transform 0.5s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.5s ease-out';
        el.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px) scale3d(1, 1, 1)';
        if (glare) {
          glare.style.opacity = '0';
        }
        bounds = null;
      });
    }

    // Initialize all existing cards
    document.querySelectorAll(selector).forEach(attachTilt);

    // Mutation observer for dynamically rendered cards (e.g. recruiter results)
    const observer = new MutationObserver(() => {
      document.querySelectorAll(selector).forEach(attachTilt);
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  // --- 2. 3D LIVE KINETIC WAVEFORM (TELEMETRY RIBBON) ---
  function init3DSearchWaveform(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = (canvas.width = canvas.parentElement.clientWidth || 600);
    let height = (canvas.height = canvas.parentElement.clientHeight || 80);
    let step = 0;

    function renderWave() {
      ctx.clearRect(0, 0, width, height);

      step += 0.04;
      const lines = 4;

      for (let l = 0; l < lines; l++) {
        ctx.beginPath();
        const freq = 0.015 + l * 0.005;
        const amp = 12 + l * 4;
        const offset = l * 1.2;

        ctx.moveTo(0, height / 2);
        for (let x = 0; x < width; x += 3) {
          const y = height / 2 + Math.sin(x * freq + step + offset) * amp * Math.sin(x / width * Math.PI);
          ctx.lineTo(x, y);
        }

        const alpha = (0.2 + (l / lines) * 0.6).toFixed(2);
        const color = l % 2 === 0 ? `rgba(56, 189, 248, ${alpha})` : `rgba(99, 102, 241, ${alpha})`;
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.shadowColor = color;
        ctx.shadowBlur = 8;
        ctx.stroke();
        ctx.shadowBlur = 0;
      }

      requestAnimationFrame(renderWave);
    }

    renderWave();

    window.addEventListener('resize', () => {
      if (!canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth || 600;
      height = canvas.height = canvas.parentElement.clientHeight || 80;
    });
  }

  // --- BOOTSTRAP 3D MODULES ON DOM READY ---
  document.addEventListener('DOMContentLoaded', () => {
    init3DCardTilt();
    init3DSearchWaveform('search-3d-waveform');
  });

  // Global triggers for scan state events
  window.triggerRadar3DScan = function (isScanning) {
    if (isScanning) {
      window.dispatchEvent(new CustomEvent('radarScanStart'));
    } else {
      window.dispatchEvent(new CustomEvent('radarScanEnd'));
    }
  };

})();
