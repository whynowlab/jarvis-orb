import * as THREE from 'three';

/**
 * Jarvis Orb — Organic sphere with event-reactive animations.
 * Blue/purple energy base + cyan holographic Jarvis touch.
 */

// Vertex shader: displacement for organic surface
const vertexShader = `
  uniform float uTime;
  uniform float uDisplacement;
  uniform float uScale;
  varying vec3 vNormal;
  varying vec3 vPosition;
  varying float vDisplacement;

  // Simplex-like noise
  vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec4 permute(vec4 x) { return mod289(((x * 34.0) + 1.0) * x); }
  vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

  float snoise(vec3 v) {
    const vec2 C = vec2(1.0 / 6.0, 1.0 / 3.0);
    const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
    vec3 i = floor(v + dot(v, C.yyy));
    vec3 x0 = v - i + dot(i, C.xxx);
    vec3 g = step(x0.yzx, x0.xyz);
    vec3 l = 1.0 - g;
    vec3 i1 = min(g.xyz, l.zxy);
    vec3 i2 = max(g.xyz, l.zxy);
    vec3 x1 = x0 - i1 + C.xxx;
    vec3 x2 = x0 - i2 + C.yyy;
    vec3 x3 = x0 - D.yyy;
    i = mod289(i);
    vec4 p = permute(permute(permute(
      i.z + vec4(0.0, i1.z, i2.z, 1.0))
      + i.y + vec4(0.0, i1.y, i2.y, 1.0))
      + i.x + vec4(0.0, i1.x, i2.x, 1.0));
    float n_ = 0.142857142857;
    vec3 ns = n_ * D.wyz - D.xzx;
    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
    vec4 x_ = floor(j * ns.z);
    vec4 y_ = floor(j - 7.0 * x_);
    vec4 x = x_ * ns.x + ns.yyyy;
    vec4 y = y_ * ns.x + ns.yyyy;
    vec4 h = 1.0 - abs(x) - abs(y);
    vec4 b0 = vec4(x.xy, y.xy);
    vec4 b1 = vec4(x.zw, y.zw);
    vec4 s0 = floor(b0) * 2.0 + 1.0;
    vec4 s1 = floor(b1) * 2.0 + 1.0;
    vec4 sh = -step(h, vec4(0.0));
    vec4 a0 = b0.xzyw + s0.xzyw * sh.xxyy;
    vec4 a1 = b1.xzyw + s1.xzyw * sh.zzww;
    vec3 p0 = vec3(a0.xy, h.x);
    vec3 p1 = vec3(a0.zw, h.y);
    vec3 p2 = vec3(a1.xy, h.z);
    vec3 p3 = vec3(a1.zw, h.w);
    vec4 norm = taylorInvSqrt(vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3)));
    p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;
    vec4 m = max(0.6 - vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)), 0.0);
    m = m * m;
    return 42.0 * dot(m*m, vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3)));
  }

  void main() {
    vNormal = normal;
    vPosition = position;

    float noise = snoise(position * 2.0 + uTime * 0.5);
    vDisplacement = noise;

    vec3 newPosition = position + normal * noise * uDisplacement;
    newPosition *= uScale;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
  }
`;

// Fragment shader: blue/purple gradient + cyan glow
const fragmentShader = `
  uniform float uTime;
  uniform vec3 uColor1;
  uniform vec3 uColor2;
  uniform vec3 uGlowColor;
  uniform float uGlowIntensity;
  uniform float uAlertMix;
  uniform vec3 uAlertColor;
  varying vec3 vNormal;
  varying vec3 vPosition;
  varying float vDisplacement;

  void main() {
    // Fresnel for edge glow
    vec3 viewDir = normalize(cameraPosition - vPosition);
    float fresnel = pow(1.0 - dot(viewDir, vNormal), 2.0);

    // Base gradient
    float gradient = (vPosition.y + 1.0) * 0.5;
    vec3 baseColor = mix(uColor1, uColor2, gradient + vDisplacement * 0.3);

    // Alert color mix
    baseColor = mix(baseColor, uAlertColor, uAlertMix);

    // Glow
    vec3 glow = uGlowColor * fresnel * uGlowIntensity;

    // Holographic shimmer
    float shimmer = sin(vPosition.x * 10.0 + uTime * 2.0) * 0.05;

    vec3 finalColor = baseColor + glow + shimmer;
    float alpha = 0.85 + fresnel * 0.15;

    gl_FragColor = vec4(finalColor, alpha);
  }
`;

export function createOrb(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.z = 3;

  // Orb uniforms
  const uniforms = {
    uTime: { value: 0 },
    uDisplacement: { value: 0.15 },
    uScale: { value: 1.0 },
    uColor1: { value: new THREE.Color(0x00F0FF) },   // Cyan
    uColor2: { value: new THREE.Color(0xBD00FF) },   // Purple
    uGlowColor: { value: new THREE.Color(0x00F0FF) }, // Cyan glow
    uGlowIntensity: { value: 0.6 },
    uAlertMix: { value: 0.0 },
    uAlertColor: { value: new THREE.Color(0xFF3366) }, // Red/orange alert
  };

  const geometry = new THREE.SphereGeometry(0.8, 64, 64);
  const material = new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms,
    transparent: true,
  });
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);

  // Sub orbs for team dispatch
  const subOrbs = [];
  for (let i = 0; i < 3; i++) {
    const subGeo = new THREE.SphereGeometry(0.25, 32, 32);
    const subMat = new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: {
        ...Object.fromEntries(
          Object.entries(uniforms).map(([k, v]) => [k, { value: v.value instanceof THREE.Color ? v.value.clone() : v.value }])
        ),
        uScale: { value: 0.0 },
      },
      transparent: true,
    });
    const subMesh = new THREE.Mesh(subGeo, subMat);
    subMesh.visible = false;
    scene.add(subMesh);
    subOrbs.push(subMesh);
  }

  // Particle system for memory_save effect
  const particleCount = 50;
  const particleGeo = new THREE.BufferGeometry();
  const particlePositions = new Float32Array(particleCount * 3);
  const particleVelocities = [];
  for (let i = 0; i < particleCount; i++) {
    particlePositions[i * 3] = 0;
    particlePositions[i * 3 + 1] = 0;
    particlePositions[i * 3 + 2] = 0;
    particleVelocities.push(new THREE.Vector3());
  }
  particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
  const particleMat = new THREE.PointsMaterial({
    color: 0x00F0FF,
    size: 0.03,
    transparent: true,
    opacity: 0,
  });
  const particles = new THREE.Points(particleGeo, particleMat);
  scene.add(particles);

  // Animation state
  let currentAnimation = null;
  let animationTime = 0;
  const clock = new THREE.Clock();

  // Target values for smooth transitions
  const targets = {
    scale: 1.0,
    displacement: 0.15,
    glowIntensity: 0.6,
    alertMix: 0.0,
  };

  function lerp(current, target, speed) {
    return current + (target - current) * speed;
  }

  function animate() {
    requestAnimationFrame(animate);

    const delta = clock.getDelta();
    const elapsed = clock.getElapsedTime();
    uniforms.uTime.value = elapsed;

    // Idle breathing
    const breathe = Math.sin(elapsed * 0.8) * 0.03 + 1.0;
    targets.scale = currentAnimation === 'idle' || !currentAnimation
      ? breathe
      : targets.scale;

    // Smooth transitions
    uniforms.uScale.value = lerp(uniforms.uScale.value, targets.scale, 0.05);
    uniforms.uDisplacement.value = lerp(uniforms.uDisplacement.value, targets.displacement, 0.05);
    uniforms.uGlowIntensity.value = lerp(uniforms.uGlowIntensity.value, targets.glowIntensity, 0.05);
    uniforms.uAlertMix.value = lerp(uniforms.uAlertMix.value, targets.alertMix, 0.05);

    // Animation timeout — return to idle
    if (currentAnimation && currentAnimation !== 'idle') {
      animationTime -= delta;
      if (animationTime <= 0) {
        resetToIdle();
      }
    }

    // Update particles
    updateParticles(delta);

    renderer.render(scene, camera);
  }

  function updateParticles(delta) {
    const positions = particles.geometry.attributes.position.array;
    for (let i = 0; i < particleCount; i++) {
      const vel = particleVelocities[i];
      positions[i * 3] += vel.x * delta;
      positions[i * 3 + 1] += vel.y * delta;
      positions[i * 3 + 2] += vel.z * delta;
      // Pull toward center
      positions[i * 3] *= 0.95;
      positions[i * 3 + 1] *= 0.95;
      positions[i * 3 + 2] *= 0.95;
    }
    particles.geometry.attributes.position.needsUpdate = true;
  }

  function emitParticles() {
    const positions = particles.geometry.attributes.position.array;
    particleMat.opacity = 0.8;
    for (let i = 0; i < particleCount; i++) {
      const angle = Math.random() * Math.PI * 2;
      const radius = 1.5 + Math.random() * 0.5;
      positions[i * 3] = Math.cos(angle) * radius;
      positions[i * 3 + 1] = (Math.random() - 0.5) * radius;
      positions[i * 3 + 2] = Math.sin(angle) * radius;
      particleVelocities[i].set(
        -positions[i * 3] * 2,
        -positions[i * 3 + 1] * 2,
        -positions[i * 3 + 2] * 2
      );
    }
    particles.geometry.attributes.position.needsUpdate = true;
    setTimeout(() => { particleMat.opacity = 0; }, 1500);
  }

  function resetToIdle() {
    currentAnimation = 'idle';
    targets.scale = 1.0;
    targets.displacement = 0.15;
    targets.glowIntensity = 0.6;
    targets.alertMix = 0.0;
    subOrbs.forEach(s => { s.visible = false; });
  }

  // Public API
  return {
    animate,
    triggerAnimation(type) {
      currentAnimation = type;
      animationTime = 2.0; // seconds before returning to idle

      switch (type) {
        case 'memory_save':
          targets.glowIntensity = 1.2;
          targets.displacement = 0.25;
          emitParticles();
          break;

        case 'memory_contradict':
          targets.alertMix = 0.8;
          targets.displacement = 0.3;
          targets.glowIntensity = 1.5;
          animationTime = 3.0;
          break;

        case 'entity_update':
          targets.displacement = 0.35;
          targets.glowIntensity = 0.9;
          break;

        case 'team_dispatch':
          targets.scale = 0.7;
          animationTime = 4.0;
          const positions = [
            [-1.2, 0.8, 0],
            [1.2, 0.8, 0],
            [0, -1.2, 0],
          ];
          subOrbs.forEach((s, i) => {
            s.visible = true;
            s.material.uniforms.uScale.value = 0.8;
            s.position.set(...positions[i]);
          });
          break;

        case 'team_result':
          subOrbs.forEach(s => {
            s.position.set(0, 0, 0);
            setTimeout(() => { s.visible = false; }, 800);
          });
          targets.scale = 1.1;
          targets.glowIntensity = 1.3;
          break;

        case 'context_compact':
          targets.scale = 0.5;
          targets.glowIntensity = 2.0;
          animationTime = 1.5;
          break;

        case 'session_start':
          targets.scale = 1.2;
          targets.glowIntensity = 1.8;
          targets.displacement = 0.3;
          animationTime = 3.0;
          break;

        case 'search':
          uniforms.uColor1.value.set(0xBD00FF); // violet
          targets.glowIntensity = 1.0;
          setTimeout(() => { uniforms.uColor1.value.set(0x00F0FF); }, 1000);
          break;

        case 'idle':
        default:
          resetToIdle();
          break;
      }
    },
    resize(w, h) {
      renderer.setSize(w, h);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    },
  };
}
