import React from 'react';
import genesysLogo from '../assets/genesys_logo.png';
import mongoDBLogo from '../assets/mongodb_logo.png';


const HLD_Architecture = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Auditing Dashboard - High Level Architecture
        </h1>
        {/* <p className="text-slate-400 text-sm">
          In-house Alternative to Pointel CMS Genesys Audit and Alert Solution
        </p> */}
      </div>

      {/* Architecture Diagram */}
      <div className="max-w-7xl mx-auto">
        <svg viewBox="0 0 1200 750" className="w-full h-auto">
          <defs>
            {/* Gradients */}
            <linearGradient id="genesysGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FF4F1F" />
              <stop offset="100%" stopColor="#FF6B35" />
            </linearGradient>
            <linearGradient id="mongoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#00ED64" />
              <stop offset="100%" stopColor="#00684A" />
            </linearGradient>
            <linearGradient id="nodeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#68A063" />
              <stop offset="100%" stopColor="#3C873A" />
            </linearGradient>
            <linearGradient id="reactGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#61DAFB" />
              <stop offset="100%" stopColor="#00D8FF" />
            </linearGradient>
            <linearGradient id="dataFlowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3B82F6" />
              <stop offset="100%" stopColor="#8B5CF6" />
            </linearGradient>
            <linearGradient id="blackchairGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#6B7280" />
              <stop offset="100%" stopColor="#4B5563" />
            </linearGradient>
            <linearGradient id="gcpGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4285F4" />
              <stop offset="25%" stopColor="#EA4335" />
              <stop offset="50%" stopColor="#FBBC04" />
              <stop offset="75%" stopColor="#34A853" />
              <stop offset="100%" stopColor="#4285F4" />
            </linearGradient>
            <linearGradient id="cloudRunGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4285F4" />
              <stop offset="100%" stopColor="#1A73E8" />
            </linearGradient>
            <linearGradient id="firebaseGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FFCA28" />
              <stop offset="100%" stopColor="#FFA000" />
            </linearGradient>

            {/* Arrow Marker */}
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#3B82F6" />
            </marker>
            <marker id="arrowheadGray" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#6B7280" />
            </marker>
            <marker id="arrowheadSmall" markerWidth="6" markerHeight="4" refX="5" refY="2" orient="auto">
              <polygon points="0 0, 6 2, 0 4" fill="#3B82F6" />
            </marker>

            {/* Glow Filter */}
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>

            {/* Shadow Filter */}
            <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="2" dy="4" stdDeviation="4" floodOpacity="0.3" />
            </filter>
          </defs>

          {/* Background Grid Pattern */}
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#475569" strokeWidth="0.7" opacity="0.5" />
          </pattern>
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* ==================== LAYER 1: DATA SOURCES ==================== */}
          <g transform="translate(50, 80)">
            {/* Section Label */}
            <text x="0" y="-20" fill="#94A3B8" fontSize="14" fontWeight="600">
              DATA SOURCES
            </text>
            <line x1="0" y1="-10" x2="200" y2="-10" stroke="#475569" strokeWidth="1" />

            {/* Genesys Cloud Box */}
            <g filter="url(#shadow)">
              <rect x="0" y="0" width="200" height="140" rx="12" fill="#1E293B" stroke="url(#genesysGradient)" strokeWidth="2" />
              
              {/* Genesys Logo */}
              <image href={genesysLogo} x="60" y="15" width="80" height="50" preserveAspectRatio="xMidYMid meet" />
              
              <text x="100" y="85" textAnchor="middle" fill="white" fontSize="14" fontWeight="600">
                Genesys Cloud
              </text>
              <text x="100" y="105" textAnchor="middle" fill="#94A3B8" fontSize="11">
                Audit APIs (GET/POST)
              </text>
              <text x="100" y="120" textAnchor="middle" fill="#94A3B8" fontSize="10">
                Real-time Audit Logs
              </text>
            </g>

            {/* Blackchair Archive Box (Discontinued) */}
            <g filter="url(#shadow)" transform="translate(0, 260)">
              <rect x="0" y="0" width="200" height="100" rx="12" fill="#1E293B" stroke="url(#blackchairGradient)" strokeWidth="2" strokeDasharray="5,5" />
              
              {/* Archive Icon */}
              <rect x="85" y="15" width="30" height="25" rx="3" fill="#6B7280" />
              <rect x="90" y="20" width="20" height="3" fill="#1E293B" />
              <rect x="90" y="26" width="20" height="3" fill="#1E293B" />
              <rect x="90" y="32" width="20" height="3" fill="#1E293B" />
              
              <text x="100" y="60" textAnchor="middle" fill="#9CA3AF" fontSize="13" fontWeight="600">
                Blackchair Archives
              </text>
              <text x="100" y="78" textAnchor="middle" fill="#6B7280" fontSize="10">
                Historical Data Only
              </text>
              <text x="100" y="92" textAnchor="middle" fill="#EF4444" fontSize="9" fontWeight="500">
                ⚠ DISCONTINUED
              </text>
            </g>
          </g>

          {/* ==================== LAYER 2: DATA PROCESSING (GCP) ==================== */}
          <g transform="translate(340, 55)">
            {/* GCP Cloud Wrapper */}
            <rect x="0" y="0" width="240" height="370" rx="16" fill="none" stroke="url(#gcpGradient)" strokeWidth="2" strokeDasharray="8,4" />
            <g transform="translate(10, -8)">
              <rect x="0" y="0" width="120" height="18" rx="9" fill="#1E293B" />
              <text x="10" y="13" fill="#4285F4" fontSize="9" fontWeight="600">☁️ Google Cloud Platform</text>
            </g>
            
            {/* Section Label */}
            <text x="10" y="30" fill="#94A3B8" fontSize="12" fontWeight="600">
              DATA INGESTION & NORMALIZATION
            </text>

            {/* Data Processor Box */}
            <g filter="url(#shadow)" transform="translate(10, 45)">
              <rect x="0" y="0" width="220" height="305" rx="12" fill="#1E293B" stroke="url(#cloudRunGradient)" strokeWidth="2" />
              
              {/* Cloud Run Badge */}
              <g transform="translate(55, 10)">
                <rect x="0" y="0" width="120" height="20" rx="10" fill="#4285F4" />
                <text x="55" y="14" textAnchor="middle" fill="white" fontSize="9" fontWeight="600">⚡ Cloud Run + Scheduler</text>
              </g>
              
              <text x="110" y="50" textAnchor="middle" fill="white" fontSize="14" fontWeight="600">
                Data Processor
              </text>
              
              {/* Tech Stack Badge */}
              <g transform="translate(35, 60)">
                <rect x="0" y="0" width="150" height="22" rx="11" fill="#0F172A" stroke="#475569" strokeWidth="1" />
                <text x="75" y="15" textAnchor="middle" fill="#94A3B8" fontSize="9">
                  🟢 Node.js  |  🐍 Python
                </text>
              </g>

              {/* Processing Steps */}
              <g transform="translate(20, 95)">
                {/* Step 1 */}
                <rect x="0" y="0" width="180" height="40" rx="6" fill="#0F172A" />
                <circle cx="20" cy="20" r="10" fill="#3B82F6" />
                <text x="20" y="24" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">1</text>
                <text x="40" y="17" fill="white" fontSize="11">Fetch Audit Logs</text>
                <text x="40" y="30" fill="#64748B" fontSize="9">via Genesys API</text>

                {/* Step 2 */}
                <rect x="0" y="50" width="180" height="40" rx="6" fill="#0F172A" />
                <circle cx="20" cy="70" r="10" fill="#8B5CF6" />
                <text x="20" y="74" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">2</text>
                <text x="40" y="67" fill="white" fontSize="11">Parse & Normalize</text>
                <text x="40" y="80" fill="#64748B" fontSize="9">Standardize schema</text>

                {/* Step 3 */}
                <rect x="0" y="100" width="180" height="40" rx="6" fill="#0F172A" />
                <circle cx="20" cy="120" r="10" fill="#10B981" />
                <text x="20" y="124" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">3</text>
                <text x="40" y="117" fill="white" fontSize="11">Enrich & Transform</text>
                <text x="40" y="130" fill="#64748B" fontSize="9">Add metadata</text>

                {/* Step 4 */}
                <rect x="0" y="150" width="180" height="40" rx="6" fill="#0F172A" />
                <circle cx="20" cy="170" r="10" fill="#F59E0B" />
                <text x="20" y="174" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">4</text>
                <text x="40" y="167" fill="white" fontSize="11">Store in MongoDB</text>
                <text x="40" y="180" fill="#64748B" fontSize="9">Persist audit records</text>
              </g>
            </g>
          </g>

          {/* ==================== LAYER 3: DATABASE ==================== */}
          <g transform="translate(660, 80)">
            {/* Section Label */}
            <text x="0" y="-20" fill="#94A3B8" fontSize="14" fontWeight="600">
              DATA STORAGE
            </text>
            <line x1="0" y1="-10" x2="200" y2="-10" stroke="#475569" strokeWidth="1" />

            {/* MongoDB Box */}
            <g filter="url(#shadow)">
              <rect x="0" y="0" width="200" height="340" rx="12" fill="#1E293B" stroke="url(#mongoGradient)" strokeWidth="2" />
              
              {/* MongoDB Logo */}
              <image href={mongoDBLogo} x="55" y="10" width="90" height="55" preserveAspectRatio="xMidYMid meet" />
              
              <text x="100" y="80" textAnchor="middle" fill="white" fontSize="14" fontWeight="600">
                MongoDB
              </text>
              <text x="100" y="96" textAnchor="middle" fill="#94A3B8" fontSize="10">
                Document Database
              </text>

              {/* Database Schema */}
              <g transform="translate(15, 110)">
                <text x="0" y="0" fill="#00ED64" fontSize="11" fontWeight="600">
                  📁 Collections Structure:
                </text>

                {/* Collection 1 */}
                <rect x="0" y="15" width="170" height="50" rx="4" fill="#0F172A" />
                <text x="10" y="33" fill="#00ED64" fontSize="10" fontWeight="500">audit_logs</text>
                <text x="10" y="48" fill="#64748B" fontSize="9">timestamp, action, userId,</text>
                <text x="10" y="58" fill="#64748B" fontSize="9">entityType, changes, source</text>

                {/* Collection 2 */}
                <rect x="0" y="72" width="170" height="45" rx="4" fill="#0F172A" />
                <text x="10" y="90" fill="#00ED64" fontSize="10" fontWeight="500">users_metadata</text>
                <text x="10" y="105" fill="#64748B" fontSize="9">userId, name, role, division</text>

                {/* Collection 3 */}
                <rect x="0" y="124" width="170" height="45" rx="4" fill="#0F172A" />
                <text x="10" y="142" fill="#00ED64" fontSize="10" fontWeight="500">blackchair_archive</text>
                <text x="10" y="157" fill="#64748B" fontSize="9">Historical data retention</text>

                {/* Collection 4 */}
                <rect x="0" y="176" width="170" height="45" rx="4" fill="#0F172A" />
                <text x="10" y="194" fill="#00ED64" fontSize="10" fontWeight="500">config_snapshots</text>
                <text x="10" y="209" fill="#64748B" fontSize="9">entity, version, config_json</text>
              </g>
            </g>
          </g>

          {/* ==================== LAYER 4 & 5: BACKEND + FRONTEND (GCP) ==================== */}
          <g transform="translate(905, 55)">
            {/* GCP Cloud Wrapper for Backend + Frontend */}
            <rect x="0" y="0" width="250" height="485" rx="16" fill="none" stroke="url(#gcpGradient)" strokeWidth="2" strokeDasharray="8,4" />
            <g transform="translate(10, -8)">
              <rect x="0" y="0" width="120" height="18" rx="9" fill="#1E293B" />
              <text x="10" y="13" fill="#4285F4" fontSize="9" fontWeight="600">☁️ Google Cloud Platform</text>
            </g>

            {/* BACKEND SERVICES */}
            <g transform="translate(10, 25)">
              {/* Section Label */}
              <text x="0" y="0" fill="#94A3B8" fontSize="12" fontWeight="600">
                BACKEND SERVICES
              </text>

              {/* Node.js Microservice Box */}
              <g filter="url(#shadow)" transform="translate(0, 15)">
                <rect x="0" y="0" width="230" height="190" rx="12" fill="#1E293B" stroke="url(#cloudRunGradient)" strokeWidth="2" />
                
                {/* Cloud Run Badge */}
                <g transform="translate(75, 8)">
                  <rect x="0" y="0" width="80" height="18" rx="9" fill="#4285F4" />
                  <text x="40" y="13" textAnchor="middle" fill="white" fontSize="8" fontWeight="600">⚡ Cloud Run</text>
                </g>
                
                {/* Node.js Icon */}
                <g transform="translate(90, 30)">
                  <polygon points="25,0 50,15 50,45 25,60 0,45 0,15" fill="url(#nodeGradient)" />
                  <text x="25" y="35" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">JS</text>
                </g>
                
                <text x="115" y="105" textAnchor="middle" fill="white" fontSize="13" fontWeight="600">
                  Node.js Microservice
                </text>
                <text x="115" y="120" textAnchor="middle" fill="#94A3B8" fontSize="9">
                  RESTful API Service
                </text>

                {/* API Endpoints */}
                <g transform="translate(15, 130)">
                  <rect x="0" y="0" width="200" height="50" rx="6" fill="#0F172A" />
                  <text x="10" y="14" fill="#68A063" fontSize="9" fontWeight="500">API Endpoints:</text>
                  <text x="10" y="27" fill="#64748B" fontSize="8">GET  /api/audit-logs</text>
                  <text x="10" y="38" fill="#64748B" fontSize="8">POST /api/audit-logs/search</text>
                </g>
              </g>
            </g>

            {/* FRONTEND APPLICATION */}
            <g transform="translate(10, 260)">
              {/* Section Label */}
              <text x="0" y="0" fill="#94A3B8" fontSize="12" fontWeight="600">
                FRONTEND APPLICATION
              </text>

              {/* React Dashboard Box */}
              <g filter="url(#shadow)" transform="translate(0, 15)">
                <rect x="0" y="0" width="230" height="195" rx="12" fill="#1E293B" stroke="url(#firebaseGradient)" strokeWidth="2" />
                
                {/* Firebase Hosting Badge */}
                <g transform="translate(60, 8)">
                  <rect x="0" y="0" width="110" height="18" rx="9" fill="url(#firebaseGradient)" />
                  <text x="55" y="13" textAnchor="middle" fill="#1E293B" fontSize="8" fontWeight="600">🔥 Firebase Hosting</text>
                </g>
                
                {/* React Icon */}
                <g transform="translate(90, 30)">
                  <ellipse cx="25" cy="25" rx="8" ry="20" fill="none" stroke="#61DAFB" strokeWidth="2" transform="rotate(0 25 25)" />
                  <ellipse cx="25" cy="25" rx="8" ry="20" fill="none" stroke="#61DAFB" strokeWidth="2" transform="rotate(60 25 25)" />
                  <ellipse cx="25" cy="25" rx="8" ry="20" fill="none" stroke="#61DAFB" strokeWidth="2" transform="rotate(-60 25 25)" />
                  <circle cx="25" cy="25" r="4" fill="#61DAFB" />
                </g>
                
                <text x="115" y="85" textAnchor="middle" fill="white" fontSize="13" fontWeight="600">
                  React Dashboard
                </text>
                <text x="115" y="100" textAnchor="middle" fill="#94A3B8" fontSize="9">
                  Interactive UI + CDN
                </text>

                {/* Dashboard Components */}
                <g transform="translate(15, 110)">
                  <rect x="0" y="0" width="100" height="30" rx="4" fill="#0F172A" />
                  <text x="50" y="13" textAnchor="middle" fill="#61DAFB" fontSize="8">📊 Audit Table</text>
                  <text x="50" y="24" textAnchor="middle" fill="#64748B" fontSize="7">Filter & Sort</text>

                  <rect x="110" y="0" width="100" height="30" rx="4" fill="#0F172A" />
                  <text x="160" y="13" textAnchor="middle" fill="#61DAFB" fontSize="8">📈 Analytics</text>
                  <text x="160" y="24" textAnchor="middle" fill="#64748B" fontSize="7">Charts</text>

                  <rect x="0" y="40" width="100" height="30" rx="4" fill="#0F172A" />
                  <text x="50" y="53" textAnchor="middle" fill="#61DAFB" fontSize="8">🔍 Search</text>
                  <text x="50" y="64" textAnchor="middle" fill="#64748B" fontSize="7">Query</text>

                  <rect x="110" y="40" width="100" height="30" rx="4" fill="#0F172A" />
                  <text x="160" y="53" textAnchor="middle" fill="#61DAFB" fontSize="8">⬇️ Export</text>
                  <text x="160" y="64" textAnchor="middle" fill="#64748B" fontSize="7">CSV/PDF</text>
                </g>
              </g>
            </g>
          </g>

          {/* ==================== DATA FLOW ARROWS ==================== */}
          {/* Genesys to Processor */}
          <g>
            <line x1="250" y1="155" x2="335" y2="190" stroke="#3B82F6" strokeWidth="3" markerEnd="url(#arrowhead)" filter="url(#glow)" />
            <text x="275" y="165" fill="#3B82F6" fontSize="9" fontWeight="500">REST API</text>
          </g>

          {/* Blackchair to MongoDB (dashed - historical only) */}
          <g>
            <path d="M 250 410 Q 520 520 660 400" fill="none" stroke="#6B7280" strokeWidth="2" strokeDasharray="5,5" markerEnd="url(#arrowheadGray)" />
            <text x="440" y="452" fill="#6B7280" fontSize="9">Historical Import</text>
          </g>

          {/* Processor to MongoDB */}  
          <g>
            <line x1="582" y1="240" x2="655" y2="250" stroke="#3B82F6" strokeWidth="3" markerEnd="url(#arrowhead)" />
            <text x="600" y="232" fill="#3B82F6" fontSize="9" fontWeight="500">Store</text>
          </g>

          {/* MongoDB to Node.js (Cloud Run) */}
          <g>
            <line x1="860" y1="250" x2="900" y2="190" stroke="#3B82F6" strokeWidth="3" markerEnd="url(#arrowhead)" filter="url(#glow)" />
            <text x="875" y="250" fill="#3B82F6" fontSize="9" fontWeight="500">Query</text>
          </g>

          {/* Node.js to React (within GCP) */}
          <g>
            <line x1="1100" y1="290" x2="1100" y2="320" stroke="#3B82F6" strokeWidth="3" markerEnd="url(#arrowhead)" />
            <text x="1115" y="310" fill="#3B82F6" fontSize="9" fontWeight="500">JSON</text>
          </g>

          {/* ==================== NOTES SECTION ==================== */}
          <g transform="translate(50, 560)">
            <rect x="0" y="0" width="1100" height="140" rx="8" fill="#0F172A" stroke="#475569" strokeWidth="1" />
            
            <text x="20" y="25" fill="#F59E0B" fontSize="13" fontWeight="600">
              📝 Architecture Notes
            </text>
            
            <line x1="20" y1="35" x2="1080" y2="35" stroke="#334155" strokeWidth="1" />
            
            <text x="20" y="55" fill="#94A3B8" fontSize="11">
              • Real-time audit log collection via Genesys Cloud Platform APIs (GET/POST). Cloud Run service scheduled to poll every 5 minutes for new logs.
            </text>
            <text x="20" y="75" fill="#94A3B8" fontSize="11">
              • MongoDB stores both actively collected Genesys audit data AND historical Blackchair archives (Blackchair is discontinued - only data retained).
            </text>
            <text x="20" y="95" fill="#94A3B8" fontSize="11">
              • Node.js microservice on GCP Cloud Run provides RESTful endpoints for querying audit data.
            </text>
            <text x="20" y="115" fill="#94A3B8" fontSize="11">
              • React dashboard hosted on Firebase Hosting with global CDN for low-latency.
            </text>
            {/* <text x="20" y="132" fill="#F97316" fontSize="10" fontWeight="500">
              ⚠ Going forward: All new audit logs will be collected directly via Genesys APIs - Blackchair integration is deprecated
            </text> */}
          </g>

          {/* Legend */}
          <g transform="translate(50, 470)">
            <rect x="0" y="0" width="420" height="70" rx="6" fill="#0F172A" stroke="#334155" strokeWidth="1" />
            <text x="15" y="20" fill="#94A3B8" fontSize="11" fontWeight="600">Legend:</text>
            
            <line x1="15" y1="38" x2="45" y2="38" stroke="#3B82F6" strokeWidth="3" />
            <text x="55" y="42" fill="#64748B" fontSize="10">Active Data Flow</text>
            
            <line x1="15" y1="55" x2="45" y2="55" stroke="#6B7280" strokeWidth="2" strokeDasharray="5,5" />
            <text x="55" y="59" fill="#64748B" fontSize="10">Historical/Deprecated</text>

            <circle cx="180" cy="38" r="6" fill="#00ED64" />
            <text x="195" y="42" fill="#64748B" fontSize="10">MongoDB</text>

            <circle cx="180" cy="55" r="6" fill="url(#genesysGradient)" />
            <text x="195" y="59" fill="#64748B" fontSize="10">Data Source</text>
            
            <rect x="270" y="32" width="60" height="14" rx="7" fill="#4285F4" />
            <text x="300" y="43" textAnchor="middle" fill="white" fontSize="8">Cloud Run</text>
            
            <rect x="340" y="32" width="70" height="14" rx="7" fill="url(#firebaseGradient)" />
            <text x="375" y="43" textAnchor="middle" fill="#1E293B" fontSize="8">Firebase</text>
            
            <rect x="270" y="50" width="140" height="14" rx="7" fill="none" stroke="url(#gcpGradient)" strokeWidth="1" strokeDasharray="4,2" />
            <text x="340" y="61" textAnchor="middle" fill="#4285F4" fontSize="8">GCP Boundary</text>
          </g>

          {/* Version Badge */}
          <g transform="translate(1050, 570)">
            <rect x="0" y="0" width="80" height="20" rx="10" fill="#1E293B" stroke="#4285F4" strokeWidth="1" />
            <text x="40" y="15" textAnchor="middle" fill="#4285F4" fontSize="11" fontWeight="600">v1.0.0</text>
          </g>

        </svg>
      </div>
    </div>
  );
};

export default HLD_Architecture;
