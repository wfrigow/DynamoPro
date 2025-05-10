declare module 'uuid' {
  export const NIL: string;
  export const parse: (uuid: string) => Uint8Array;
  export const stringify: (buffer: Uint8Array, offset?: number) => string;
  export const v1: (options?: any, buffer?: any, offset?: number) => string;
  export const v3: (name: string | Uint8Array, namespace: string | Uint8Array) => string;
  export const v4: (options?: any, buffer?: any, offset?: number) => string;
  export const v5: (name: string | Uint8Array, namespace: string | Uint8Array) => string;
  export const validate: (uuid: string) => boolean;
  export const version: (uuid: string) => number;
}
