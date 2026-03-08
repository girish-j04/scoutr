"use client";

import { motion } from "framer-motion";
import { FORMATION_POSITIONS, HEATMAP_ZONE_COORDS } from "@/lib/constants";

interface PitchDiagramProps {
  formation: string;
  heatmapZones: string[];
  highlightPosition?: string;
}

export default function PitchDiagram({
  formation,
  heatmapZones,
  highlightPosition = "LB",
}: PitchDiagramProps) {
  const positions = FORMATION_POSITIONS[formation] || FORMATION_POSITIONS["4-3-3"];

  return (
    <div className="relative w-full aspect-[3/4] max-w-[280px]">
      <svg viewBox="0 0 100 130" className="w-full h-full">
        {/* Pitch background */}
        <rect x="0" y="0" width="100" height="130" rx="2" fill="#1A3A28" />

        {/* Pitch markings */}
        <rect x="5" y="5" width="90" height="120" rx="1" fill="none" stroke="#E8E6E1" strokeWidth="0.4" opacity="0.3" />
        <line x1="5" y1="65" x2="95" y2="65" stroke="#E8E6E1" strokeWidth="0.4" opacity="0.3" />
        <circle cx="50" cy="65" r="12" fill="none" stroke="#E8E6E1" strokeWidth="0.4" opacity="0.3" />
        <circle cx="50" cy="65" r="0.8" fill="#E8E6E1" opacity="0.3" />

        {/* Penalty areas */}
        <rect x="25" y="5" width="50" height="20" fill="none" stroke="#E8E6E1" strokeWidth="0.4" opacity="0.3" />
        <rect x="35" y="5" width="30" height="8" fill="none" stroke="#E8E6E1" strokeWidth="0.4" opacity="0.3" />
        <rect x="25" y="105" width="50" height="20" fill="none" stroke="#E8E6E1" strokeWidth="0.4" opacity="0.3" />
        <rect x="35" y="117" width="30" height="8" fill="none" stroke="#E8E6E1" strokeWidth="0.4" opacity="0.3" />

        {/* Corner arcs */}
        <path d="M5 8 A3 3 0 0 1 8 5" fill="none" stroke="#E8E6E1" strokeWidth="0.4" opacity="0.3" />
        <path d="M92 5 A3 3 0 0 1 95 8" fill="none" stroke="#E8E6E1" strokeWidth="0.4" opacity="0.3" />
        <path d="M5 122 A3 3 0 0 0 8 125" fill="none" stroke="#E8E6E1" strokeWidth="0.4" opacity="0.3" />
        <path d="M92 125 A3 3 0 0 0 95 122" fill="none" stroke="#E8E6E1" strokeWidth="0.4" opacity="0.3" />

        {/* Heatmap zones */}
        {heatmapZones.map((zone, i) => {
          const coords = HEATMAP_ZONE_COORDS[zone];
          if (!coords) return null;
          return (
            <motion.ellipse
              key={zone}
              cx={coords.cx}
              cy={coords.cy}
              initial={{ rx: 0, ry: 0, opacity: 0 }}
              animate={{ rx: coords.rx, ry: coords.ry, opacity: 0.45 }}
              transition={{ duration: 0.8, delay: 0.3 + i * 0.2, ease: "easeOut" }}
              fill="url(#heatGradient)"
            />
          );
        })}

        {/* Formation positions */}
        {positions.map((pos, i) => {
          const isHighlight = pos.label === highlightPosition;
          return (
            <g key={i}>
              <motion.circle
                cx={pos.x}
                cy={pos.y}
                r={isHighlight ? 3.5 : 2.5}
                fill={isHighlight ? "#D4A843" : "#E8E6E1"}
                opacity={isHighlight ? 1 : 0.5}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.1 + i * 0.04, type: "spring", stiffness: 400 }}
              />
              <text
                x={pos.x}
                y={pos.y + (pos.y < 50 ? -5 : 6.5)}
                textAnchor="middle"
                fontSize="3.5"
                fill={isHighlight ? "#D4A843" : "#E8E6E1"}
                opacity={isHighlight ? 1 : 0.4}
                fontFamily="monospace"
                fontWeight={isHighlight ? "bold" : "normal"}
              >
                {pos.label}
              </text>
            </g>
          );
        })}

        {/* Gradient definitions */}
        <defs>
          <radialGradient id="heatGradient">
            <stop offset="0%" stopColor="#D4A843" stopOpacity="0.6" />
            <stop offset="50%" stopColor="#D4A843" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#D4A843" stopOpacity="0" />
          </radialGradient>
        </defs>
      </svg>
    </div>
  );
}
