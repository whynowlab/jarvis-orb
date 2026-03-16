import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

/**
 * Jarvis Orb v3 — Premium quality. Less is more.
 * Desaturated cyan/purple + subtle bloom + minimal particles.
 */

const vertexShader = `
  uniform float uTime;
  uniform float uDisplacement;
  uniform float uScale;
  varying vec3 vNormal;
  varying vec3 vPosition;
  varying float vDisplacement;

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

    // Single octave — smooth, not busy
    float noise = snoise(position * 1.8 + uTime * 0.3);
    vDisplacement = noise;

    vec3 newPosition = position + normal * noise * uDisplacement;
    newPosition *= uScale;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
  }
`;

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
    vec3 viewDir = normalize(cameraPosition - vPosition);
    // Gentle fresnel — not aggressive
    float fresnel = pow(1.0 - max(dot(viewDir, vNormal), 0.0), 2.0);

    // Smooth gradient
    float gradient = (vPosition.y + 1.0) * 0.5;
    vec3 baseColor = mix(uColor1, uColor2, gradient + vDisplacement * 0.15);

    // Alert overlay
    baseColor = mix(baseColor, uAlertColor, uAlertMix);

    // Subtle edge glow only
    vec3 glow = uGlowColor * fresnel * uGlowIntensity;

    // Holographic iridescence — shifts with position + viewing angle
    float iriBase = fresnel * 0.3 + 0.05;
    float iriPhase = vPosition.y * 4.0 + vPosition.x * 3.0 + uTime * 0.6;
    vec3 iriColor = vec3(
      sin(iriPhase) * iriBase,
      sin(iriPhase + 2.094) * iriBase,
      sin(iriPhase + 4.189) * iriBase
    );

    vec3 finalColor = baseColor + glow + iriColor;
    float alpha = 0.9;

    gl_FragColor = vec4(finalColor, alpha);
  }
`;

export function createOrb(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.7;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.z = 3;

  // Bloom — barely visible, just softens edges
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(canvas.clientWidth, canvas.clientHeight),
    0.12,  // very subtle
    1.0,   // wide radius for softness
    0.8    // high threshold
  );
  composer.addPass(bloomPass);

  // === Main Orb — desaturated colors ===
  const uniforms = {
    uTime: { value: 0 },
    uDisplacement: { value: 0.08 },   // subtle surface movement
    uScale: { value: 1.0 },
    uColor1: { value: new THREE.Color(0x4A9EBF) },   // Muted teal (desaturated cyan)
    uColor2: { value: new THREE.Color(0x6B4FA0) },   // Muted purple (desaturated)
    uGlowColor: { value: new THREE.Color(0x5BB8D4) }, // Soft cyan glow
    uGlowIntensity: { value: 0.3 },   // gentle
    uAlertMix: { value: 0.0 },
    uAlertColor: { value: new THREE.Color(0xCC4466) }, // Muted red
  };

  const geometry = new THREE.SphereGeometry(0.75, 128, 128);
  const material = new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms,
    transparent: true,
  });
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);

  // === Ambient particles — fewer, subtler ===
  const ambientCount = 30;  // was 80, now 30
  const ambientGeo = new THREE.BufferGeometry();
  const ambientPos = new Float32Array(ambientCount * 3);
  const ambientSpeeds = [];
  for (let i = 0; i < ambientCount; i++) {
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const r = 1.1 + Math.random() * 0.6;
    ambientPos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
    ambientPos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    ambientPos[i * 3 + 2] = r * Math.cos(phi);
    ambientSpeeds.push(0.1 + Math.random() * 0.3);  // slower
  }
  ambientGeo.setAttribute('position', new THREE.BufferAttribute(ambientPos, 3));
  const ambientMat = new THREE.PointsMaterial({
    color: 0x5BB8D4,   // match glow color
    size: 0.01,         // smaller
    transparent: true,
    opacity: 0.25,      // dimmer
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
  const ambientParticles = new THREE.Points(ambientGeo, ambientMat);
  scene.add(ambientParticles);

  // === Sub orbs for team dispatch ===
  const subOrbs = [];
  for (let i = 0; i < 3; i++) {
    const subGeo = new THREE.SphereGeometry(0.2, 48, 48);
    const subMat = new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: {
        ...Object.fromEntries(
          Object.entries(uniforms).map(([k, v]) => [k, { value: v.value instanceof THREE.Color ? v.value.clone() : v.value }])
        ),
        uScale: { value: 0.0 },
        uDisplacement: { value: 0.06 },
      },
      transparent: true,
    });
    const subMesh = new THREE.Mesh(subGeo, subMat);
    subMesh.visible = false;
    scene.add(subMesh);
    subOrbs.push(subMesh);
  }

  // === Event particles (memory_save) ===
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
    color: 0x80E0FF,
    size: 0.05,
    transparent: true,
    opacity: 0,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
  const particles = new THREE.Points(particleGeo, particleMat);
  scene.add(particles);

  // === Animation state ===
  let currentAnimation = null;
  let animationTime = 0;
  const clock = new THREE.Clock();
  const targets = {
    scale: 1.0,
    displacement: 0.08,
    glowIntensity: 0.3,
    alertMix: 0.0,
    bloomStrength: 0.12,
  };

  function lerp(a, b, t) { return a + (b - a) * t; }

  function animate() {
    requestAnimationFrame(animate);

    const delta = clock.getDelta();
    const elapsed = clock.getElapsedTime();
    uniforms.uTime.value = elapsed;

    // Very slow rotation
    mesh.rotation.y = elapsed * 0.06;
    mesh.rotation.x = Math.sin(elapsed * 0.03) * 0.05;

    // Gentle breathing
    const breathe = Math.sin(elapsed * 0.6) * 0.025 + 1.0;
    if (!currentAnimation || currentAnimation === 'idle') {
      targets.scale = breathe;
    }

    // Smooth transitions (slower lerp = more graceful)
    uniforms.uScale.value = lerp(uniforms.uScale.value, targets.scale, 0.03);
    uniforms.uDisplacement.value = lerp(uniforms.uDisplacement.value, targets.displacement, 0.03);
    uniforms.uGlowIntensity.value = lerp(uniforms.uGlowIntensity.value, targets.glowIntensity, 0.03);
    uniforms.uAlertMix.value = lerp(uniforms.uAlertMix.value, targets.alertMix, 0.03);
    bloomPass.strength = lerp(bloomPass.strength, targets.bloomStrength, 0.03);

    // Ambient particles — slow orbit
    const aPos = ambientParticles.geometry.attributes.position.array;
    for (let i = 0; i < ambientCount; i++) {
      const speed = ambientSpeeds[i];
      const x = aPos[i * 3];
      const z = aPos[i * 3 + 2];
      const angle = Math.atan2(z, x) + speed * delta * 0.15;
      const r = Math.sqrt(x * x + z * z);
      aPos[i * 3] = Math.cos(angle) * r;
      aPos[i * 3 + 2] = Math.sin(angle) * r;
    }
    ambientParticles.geometry.attributes.position.needsUpdate = true;

    // Sub orbs
    subOrbs.forEach((s, i) => {
      if (s.visible) {
        s.material.uniforms.uTime.value = elapsed;
      }
    });

    // Animation timeout
    if (currentAnimation && currentAnimation !== 'idle') {
      animationTime -= delta;
      if (animationTime <= 0) resetToIdle();
    }

    updateParticles(delta);
    composer.render();
  }

  function updateParticles(delta) {
    const pos = particles.geometry.attributes.position.array;
    for (let i = 0; i < particleCount; i++) {
      const vel = particleVelocities[i];
      pos[i * 3] += vel.x * delta;
      pos[i * 3 + 1] += vel.y * delta;
      pos[i * 3 + 2] += vel.z * delta;
      pos[i * 3] *= 0.985;
      pos[i * 3 + 1] *= 0.985;
      pos[i * 3 + 2] *= 0.985;
    }
    particles.geometry.attributes.position.needsUpdate = true;
    if (particleMat.opacity > 0) particleMat.opacity *= 0.992;
  }

  function emitParticles() {
    const pos = particles.geometry.attributes.position.array;
    particleMat.opacity = 0.8;
    for (let i = 0; i < particleCount; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 1.8 + Math.random() * 0.6;  // start farther out
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);
      // Slower inward velocity — so you see the trajectory
      particleVelocities[i].set(
        -pos[i * 3] * 1.2,
        -pos[i * 3 + 1] * 1.2,
        -pos[i * 3 + 2] * 1.2
      );
    }
    particles.geometry.attributes.position.needsUpdate = true;
  }

  function resetToIdle() {
    currentAnimation = 'idle';
    targets.scale = 1.0;
    targets.displacement = 0.08;
    targets.glowIntensity = 0.3;
    targets.alertMix = 0.0;
    targets.bloomStrength = 0.12;
    uniforms.uColor1.value.set(0x4A9EBF);
    uniforms.uColor2.value.set(0x6B4FA0);
    subOrbs.forEach(s => { s.visible = false; });
  }

  return {
    animate,
    triggerAnimation(type) {
      currentAnimation = type;
      animationTime = 2.5;

      switch (type) {
        case 'memory_save':
          targets.glowIntensity = 0.8;
          targets.displacement = 0.22;
          targets.scale = 1.1;
          targets.bloomStrength = 0.25;
          emitParticles();
          animationTime = 3.0;
          break;

        case 'memory_contradict':
          targets.alertMix = 0.8;
          targets.displacement = 0.28;
          targets.glowIntensity = 0.7;
          targets.bloomStrength = 0.3;
          targets.scale = 1.05;
          animationTime = 3.5;
          break;

        case 'entity_update':
          // Visible pulse — scale up then back + color shift to bright cyan
          targets.scale = 1.15;
          targets.displacement = 0.25;
          targets.glowIntensity = 0.7;
          targets.bloomStrength = 0.2;
          uniforms.uColor1.value.set(0x00D4FF);  // bright cyan flash
          animationTime = 2.5;
          break;

        case 'team_dispatch':
          targets.scale = 0.7;
          animationTime = 4.0;
          const positions = [[-1.0, 0.6, 0], [1.0, 0.6, 0], [0, -0.9, 0]];
          subOrbs.forEach((s, i) => {
            s.visible = true;
            s.material.uniforms.uScale.value = 0.7;
            s.position.set(...positions[i]);
          });
          break;

        case 'team_result':
          subOrbs.forEach(s => {
            s.position.lerp(new THREE.Vector3(0, 0, 0), 0.1);
            setTimeout(() => { s.visible = false; }, 1000);
          });
          targets.scale = 1.15;
          targets.glowIntensity = 0.7;
          targets.bloomStrength = 0.25;
          emitParticles();
          break;

        case 'context_compact':
          targets.scale = 0.45;
          targets.glowIntensity = 0.9;
          targets.displacement = 0.03;
          targets.bloomStrength = 0.3;
          animationTime = 2.5;
          break;

        case 'session_start':
          targets.scale = 1.2;
          targets.glowIntensity = 0.8;
          targets.displacement = 0.2;
          targets.bloomStrength = 0.25;
          animationTime = 3.0;
          emitParticles();
          break;

        case 'search':
          // Visible violet shift + pulse
          uniforms.uColor1.value.set(0x9B60FF);  // bright violet
          uniforms.uColor2.value.set(0xBB80FF);  // lighter violet
          targets.scale = 0.9;
          targets.glowIntensity = 0.7;
          targets.displacement = 0.18;
          targets.bloomStrength = 0.2;
          animationTime = 2.5;
          break;

        case 'idle':
        default:
          resetToIdle();
          break;
      }
    },
    resize(w, h) {
      renderer.setSize(w, h);
      composer.setSize(w, h);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    },
  };
}
