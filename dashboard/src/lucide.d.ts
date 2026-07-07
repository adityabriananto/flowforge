declare module 'lucide-react' {
  import { FC, SVGProps } from 'react';
  export interface IconProps extends SVGProps<SVGSVGElement> {
    size?: string | number;
    color?: string;
    strokeWidth?: string | number;
  }
  export type Icon = FC<IconProps>;
  
  export const Activity: Icon;
  export const Shield: Icon;
  export const Terminal: Icon;
  export const ArrowRight: Icon;
  export const CheckCircle: Icon;
  export const AlertCircle: Icon;
}
