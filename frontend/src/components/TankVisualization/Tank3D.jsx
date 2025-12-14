import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { MeshWobbleMaterial, OrbitControls, Text3D } from '@react-three/drei';
import * as THREE from 'three';


const Tank3D = ({ tankState }) => {
  const waterLevel = tankState.water_level;
  const temperature = tankState.temperature;
  const pressure = tankState.pressure;

  // لون المياه بناءً على درجة الحرارة
  const getWaterColor = (temp) => {
    if (temp < 10) return '#4d79ff'; // أزرق بارد
    if (temp < 25) return '#3399ff'; // أزرق معتدل
    if (temp < 35) return '#00ccff'; // أزرق دافئ
    return '#ff9900'; // برتقالي ساخن
  };

  return (
    <div className="w-full h-96 rounded-xl overflow-hidden">
      <Canvas camera={{ position: [0, 2, 5], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        
        {/* الخزان الخارجي */}
        <TankBase waterLevel={waterLevel} temperature={temperature} pressure={pressure} />
        
        {/* المياه داخل الخزان */}
        <Water waterLevel={waterLevel} color={getWaterColor(temperature)} />
        
        {/* المؤشرات */}
        <Indicators waterLevel={waterLevel} />
        
        {/* عناصر التحكم */}
        <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
      </Canvas>
    </div>
  );
};

const TankBase = ({ waterLevel, temperature, pressure }) => {
  const tankRef = useRef();
  
  useFrame((state) => {
    if (tankRef.current) {
      // تأثير اهتزاز خفيف عند ارتفاع الضغط
      const pressureEffect = Math.sin(state.clock.elapsedTime * 2) * (pressure - 1) * 0.01;
      tankRef.current.scale.x = 1 + pressureEffect;
      tankRef.current.scale.z = 1 + pressureEffect;
    }
  });

  return (
    <group ref={tankRef}>
      {/* جدران الخزان */}
      <mesh position={[0, 1, 0]} castShadow>
        <cylinderGeometry args={[1.5, 1.5, 2, 32]} />
        <meshStandardMaterial 
          color="#cccccc" 
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>

      {/* قاع الخزان */}
      <mesh position={[0, 0, 0]} receiveShadow>
        <cylinderGeometry args={[1.5, 1.5, 0.1, 32]} />
        <meshStandardMaterial color="#888888" />
      </mesh>

      {/* غطاء الخزان */}
      <mesh position={[0, 2, 0]}>
        <cylinderGeometry args={[1.6, 1.6, 0.1, 32]} />
        <meshStandardMaterial color="#aaaaaa" transparent opacity={0.7} />
      </mesh>
    </group>
  );
};

const Water = ({ waterLevel, color }) => {
  const waterRef = useRef();
  const waterHeight = (waterLevel / 100) * 2; // ارتفاع المياه كنسبة من ارتفاع الخزان
  
  useFrame((state) => {
    if (waterRef.current) {
      // تأثير تموج المياه
      waterRef.current.position.y = waterHeight / 2;
      const time = state.clock.elapsedTime;
      waterRef.current.scale.x = 1 + Math.sin(time) * 0.01;
      waterRef.current.scale.z = 1 + Math.cos(time * 1.1) * 0.01;
    }
  });

  return (
    <mesh ref={waterRef} position={[0, waterHeight / 2, 0]}>
      <cylinderGeometry args={[1.45, 1.45, waterHeight, 32]} />
      <MeshWobbleMaterial
        color={color}
        roughness={0.1}
        metalness={0.3}
        transparent
        opacity={0.9}
        speed={1}
        factor={0.1}
      />
    </mesh>
  );
};

const Indicators = ({ waterLevel }) => {
  const level = waterLevel.toFixed(1);
  
  return (
    <group>
      {/* مؤشر مستوى المياه */}
      <Text3D
        font="/fonts/helvetiker_regular.typeface.json"
        size={0.2}
        height={0.05}
        position={[-1.8, 1, 0]}
        rotation={[0, Math.PI / 2, 0]}
      >
        {`${level}%`}
        <meshNormalMaterial />
      </Text3D>

      {/* خطوط القياس */}
      {[0, 25, 50, 75, 100].map((level) => {
        const yPos = (level / 100) * 2;
        return (
          <group key={level} position={[1.6, yPos, 0]}>
            <mesh>
              <boxGeometry args={[0.1, 0.02, 0.3]} />
              <meshBasicMaterial color="white" />
            </mesh>
            <Text3D
              font="/fonts/helvetiker_regular.typeface.json"
              size={0.1}
              height={0.02}
              position={[0.15, 0, 0]}
              rotation={[0, Math.PI / 2, 0]}
            >
              {`${level}%`}
              <meshBasicMaterial color="white" />
            </Text3D>
          </group>
        );
      })}
    </group>
  );
};

export default Tank3D;