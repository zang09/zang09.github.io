---
layout: page
title: MH-3DGS Video Compare
permalink: /mh-3dgs-compare/
description: Split-screen before/after video comparison.
before_after_video: true
---

<div id="bal_comparison" class="bal-container-small" style="height: 460px;">
  <div class="bal-after">
    <video
      autoplay
      muted
      loop
      playsinline
      preload="metadata"
      poster="{{ '/assets/img/publication_preview/mh-3dgs.jpg' | relative_url }}"
    >
      <source src="{{ '/assets/video/mh-3dgs/mh-3dgs-after.mp4' | relative_url }}" type="video/mp4">
    </video>
    <div class="bal-afterPosition">Dataset Calib.</div>
  </div>

  <div class="bal-before">
    <div class="bal-before-inset">
      <video
        autoplay
        muted
        loop
        playsinline
        preload="metadata"
        poster="{{ '/assets/img/publication_preview/mh-3dgs.jpg' | relative_url }}"
      >
        <source src="{{ '/assets/video/mh-3dgs/mh-3dgs-before.mp4' | relative_url }}" type="video/mp4">
      </video>
    </div>
    <div class="bal-beforePosition">Ours</div>
  </div>

  <div class="bal-handle" aria-hidden="true"></div>
</div>

<p class="mt-3 mb-0">마우스 또는 터치로 중앙 핸들을 좌우로 드래그해서 비교할 수 있습니다.</p>
