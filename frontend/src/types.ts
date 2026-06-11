export type Source = {
  id: string;
  score?: number | null;
  text: string;
  metadata?: Record<string, unknown>;
};
