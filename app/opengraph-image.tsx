import { ImageResponse } from 'next/og';

export const alt = 'Growth Lab — Your coding agent, from code to market';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

export default function OpenGraphImage() {
  return new ImageResponse(
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', background: '#eaf3ff', color: '#071a2b', padding: '64px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 18, fontSize: 28, fontWeight: 700 }}>
        <div style={{ width: 54, height: 54, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#2667ff', color: 'white' }}>GL</div>
        Growth Lab
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
        <div style={{ fontSize: 74, lineHeight: 1.02, fontWeight: 750, letterSpacing: '-4px', maxWidth: 900 }}>Your coding agent can ship growth.</div>
        <div style={{ fontSize: 25, color: '#40536a' }}>Code → demand → execution → evidence → memory</div>
      </div>
      <div style={{ display: 'flex', gap: 12 }}>{['CODE', 'DEMAND', 'SHIP', 'SIGNAL', 'MEMORY'].map((label, index) => <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 12 }}><span style={{ width: 14, height: 14, borderRadius: 99, background: index === 4 ? '#ff6846' : '#2667ff' }} /><span style={{ fontSize: 18, fontFamily: 'monospace' }}>{label}</span></div>)}</div>
    </div>,
    size
  );
}
