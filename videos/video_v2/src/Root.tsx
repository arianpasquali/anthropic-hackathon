import {Composition} from 'remotion';
import {KavelPitch} from './KavelPitch';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="KavelPitch"
        component={KavelPitch}
        durationInFrames={5134}
        fps={60}
        width={1640}
        height={1118}
        defaultProps={{}}
      />
    </>
  );
};
