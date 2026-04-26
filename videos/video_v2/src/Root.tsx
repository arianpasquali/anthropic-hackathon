import {Composition} from 'remotion';
import {KavelPitch} from './KavelPitch';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="KavelPitch"
        component={KavelPitch}
        durationInFrames={150 * 30}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{}}
      />
    </>
  );
};
