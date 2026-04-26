import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate} from 'remotion';

export const KavelPitch: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const opacity = interpolate(frame, [0, fps], [0, 1], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill
      style={{
        background: '#0c1420',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        gap: 24,
      }}
    >
      <div
        style={{
          opacity,
          color: '#ffffff',
          fontSize: 72,
          fontFamily: 'sans-serif',
          fontWeight: 700,
        }}
      >
        Kavel
      </div>
      <div
        style={{
          opacity,
          color: '#6ee7b7',
          fontSize: 28,
          fontFamily: 'sans-serif',
        }}
      >
        Climate contribution for Dutch corporates
      </div>
    </AbsoluteFill>
  );
};
