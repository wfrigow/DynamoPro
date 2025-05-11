// src/types/dynamo-speech.d.ts

// Define all necessary interfaces with unique names to avoid conflicts
interface DynamoSpeechRecognitionAlternative {
  readonly transcript: string;
  readonly confidence: number;
}

interface DynamoSpeechRecognitionResult {
  readonly length: number;
  item(index: number): DynamoSpeechRecognitionAlternative;
  [index: number]: DynamoSpeechRecognitionAlternative;
  readonly isFinal: boolean;
}

interface DynamoSpeechRecognitionResultList {
  readonly length: number;
  item(index: number): DynamoSpeechRecognitionResult;
  [index: number]: DynamoSpeechRecognitionResult;
}

interface DynamoSpeechRecognitionEvent extends Event {
  readonly resultIndex: number;
  readonly results: DynamoSpeechRecognitionResultList;
}

// Define the interface for an INSTANCE of SpeechRecognition
interface DynamoSpeechRecognitionInstance extends EventTarget {
  grammars: any;
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  serviceURI?: string;

  start(): void;
  stop(): void;
  abort(): void;

  onaudiostart: ((this: DynamoSpeechRecognitionInstance, ev: Event) => any) | null;
  onsoundstart: ((this: DynamoSpeechRecognitionInstance, ev: Event) => any) | null;
  onspeechstart: ((this: DynamoSpeechRecognitionInstance, ev: Event) => any) | null;
  onspeechend: ((this: DynamoSpeechRecognitionInstance, ev: Event) => any) | null;
  onsoundend: ((this: DynamoSpeechRecognitionInstance, ev: Event) => any) | null;
  onaudioend: ((this: DynamoSpeechRecognitionInstance, ev: Event) => any) | null;
  onresult: ((this: DynamoSpeechRecognitionInstance, ev: DynamoSpeechRecognitionEvent) => any) | null;
  onnomatch: ((this: DynamoSpeechRecognitionInstance, ev: DynamoSpeechRecognitionEvent) => any) | null;
  onerror: ((this: DynamoSpeechRecognitionInstance, ev: Event) => any) | null;
  onstart: ((this: DynamoSpeechRecognitionInstance, ev: Event) => any) | null;
  onend: ((this: DynamoSpeechRecognitionInstance, ev: Event) => any) | null;
}

// Define the constructor interface
interface DynamoSpeechRecognitionConstructor {
  new(): DynamoSpeechRecognitionInstance;
  prototype: DynamoSpeechRecognitionInstance;
}

// Add to Window interface without using the same names as built-in types
declare global {
  interface Window {
    SpeechRecognition: DynamoSpeechRecognitionConstructor;
    webkitSpeechRecognition: DynamoSpeechRecognitionConstructor;
  }
}

// Make this a module
export {};
