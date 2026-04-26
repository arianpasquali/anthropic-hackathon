import {AbsoluteFill, Audio, Video, staticFile} from 'remotion';

export const KavelPitch: React.FC = () => {
  return (
    <AbsoluteFill>
      <Video
        src={staticFile('4k_recording.mov')}
        style={{width: '100%', height: '100%', objectFit: 'cover'}}
      />
      <Audio src={staticFile('Kavel-demo.m4a')} />
    </AbsoluteFill>
  );
};
