<!DOCTYPE html>
<html>
<head>
  <title>Retail Intelligence Platform</title>
  <style>
    body { margin: 0; overflow: hidden; background: #0b0f1a; }
    .hero-text {
      position: absolute;
      top: 35%;
      left: 8%;
      color: white;
      z-index: 10;
      font-family: system-ui;
    }
    .hero-text h1 { font-size: 3rem; }
    .hero-text p { opacity: 0.8; max-width: 500px; }
  </style>
</head>
<body>

<div class="hero-text">
  <h1>An AI that understands your business</h1>
  <p>
    Signals → Intelligence → Decisions.<br>
    Not dashboards. Not chatbots. Real reasoning.
  </p>
</div>

<canvas id="bg"></canvas>

<script src="https://unpkg.com/three@0.160.0/build/three.min.js"></script>
<script src="https://unpkg.com/gsap@3/dist/gsap.min.js"></script>
<script src="{% static 'js/home_3d.js' %}"></script>

</body>
</html>
