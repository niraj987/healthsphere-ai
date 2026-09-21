import { useEffect, useRef } from "react";
import * as THREE from "three";

/**
 * A rotating particle sphere ("health data network") with a soft-pulsing
 * core, plus faint connecting lines that drift — meant to read as
 * "AI analyzing a network of health signals" without depicting anything
 * medically literal (no anatomy, no diagnostic imagery).
 */
export default function HeroScene({ className = "" }) {
  const mountRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const width = mount.clientWidth;
    const height = mount.clientHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 100);
    camera.position.set(0, 0, 7.5);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(width, height);
    mount.appendChild(renderer.domElement);

    // --- Particle sphere (health data network) ---
    const PARTICLE_COUNT = 420;
    const positions = new Float32Array(PARTICLE_COUNT * 3);
    const radius = 2.6;
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const phi = Math.acos(-1 + (2 * i) / PARTICLE_COUNT);
      const theta = Math.sqrt(PARTICLE_COUNT * Math.PI) * phi;
      const x = radius * Math.cos(theta) * Math.sin(phi);
      const y = radius * Math.sin(theta) * Math.sin(phi);
      const z = radius * Math.cos(phi);
      positions.set([x, y, z], i * 3);
    }
    const particleGeometry = new THREE.BufferGeometry();
    particleGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));

    const particleMaterial = new THREE.PointsMaterial({
      color: 0x4ba898,
      size: 0.05,
      transparent: true,
      opacity: 0.85,
      sizeAttenuation: true,
    });
    const particles = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particles);

    // --- Wireframe inner sphere (structure / "platform") ---
    const wireGeometry = new THREE.IcosahedronGeometry(1.7, 1);
    const wireMaterial = new THREE.MeshBasicMaterial({
      color: 0xf2590f,
      wireframe: true,
      transparent: true,
      opacity: 0.22,
    });
    const wireSphere = new THREE.Mesh(wireGeometry, wireMaterial);
    scene.add(wireSphere);

    // --- Pulsing core ---
    const coreGeometry = new THREE.SphereGeometry(0.45, 32, 32);
    const coreMaterial = new THREE.MeshBasicMaterial({ color: 0x2f8b7c, transparent: true, opacity: 0.9 });
    const core = new THREE.Mesh(coreGeometry, coreMaterial);
    scene.add(core);

    // --- Sparse connecting lines between nearby particles for a "network" feel ---
    const linePositions = [];
    for (let i = 0; i < PARTICLE_COUNT; i += 7) {
      const a = new THREE.Vector3().fromArray(positions, i * 3);
      const j = (i + 37) % PARTICLE_COUNT;
      const b = new THREE.Vector3().fromArray(positions, j * 3);
      linePositions.push(a.x, a.y, a.z, b.x, b.y, b.z);
    }
    const lineGeometry = new THREE.BufferGeometry();
    lineGeometry.setAttribute("position", new THREE.BufferAttribute(new Float32Array(linePositions), 3));
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0x79c3b7, transparent: true, opacity: 0.15 });
    const lines = new THREE.LineSegments(lineGeometry, lineMaterial);
    scene.add(lines);

    let frameId;
    const clock = new THREE.Clock();

    const animate = () => {
      const t = clock.getElapsedTime();
      particles.rotation.y = t * 0.08;
      particles.rotation.x = Math.sin(t * 0.05) * 0.1;
      wireSphere.rotation.y = -t * 0.05;
      wireSphere.rotation.x = t * 0.03;
      lines.rotation.y = t * 0.08;
      const pulse = 1 + Math.sin(t * 1.6) * 0.12;
      core.scale.setScalar(pulse);

      renderer.render(scene, camera);
      frameId = requestAnimationFrame(animate);
    };
    animate();

    const handleResize = () => {
      const w = mount.clientWidth;
      const h = mount.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(frameId);
      window.removeEventListener("resize", handleResize);
      mount.removeChild(renderer.domElement);
      particleGeometry.dispose();
      particleMaterial.dispose();
      wireGeometry.dispose();
      wireMaterial.dispose();
      coreGeometry.dispose();
      coreMaterial.dispose();
      lineGeometry.dispose();
      lineMaterial.dispose();
      renderer.dispose();
    };
  }, []);

  return <div ref={mountRef} className={className} />;
}
