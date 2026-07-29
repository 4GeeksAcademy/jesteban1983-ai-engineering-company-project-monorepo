// lib/use-async.ts — Hook genérico de 3 estados (loading/success/error)
//
// Propósito: Encapsular el patrón de 3 estados para operaciones asíncronas.
// Cada llamada a execute() resetea el estado y maneja loading/error automáticamente.
// finally ya limpia isLoading internamente (R10).
//
// Uso:
//   const { data, isLoading, error, execute } = useAsync(fetchIncidents);
//   useEffect(() => { execute(); }, []);

import { useState, useCallback } from "react";

type AsyncState<T> = {
  data: T | null;
  isLoading: boolean;
  error: string | null;
};

type UseAsyncReturn<T> = AsyncState<T> & {
  execute: (...args: unknown[]) => Promise<T | undefined>;
};

export function useAsync<T>(
  asyncFn: (...args: unknown[]) => Promise<T>,
): UseAsyncReturn<T> {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    isLoading: false,
    error: null,
  });

  const execute = useCallback(
    async (...args: unknown[]): Promise<T | undefined> => {
      setState({ data: null, isLoading: true, error: null });
      try {
        const result = await asyncFn(...args);
        setState({ data: result, isLoading: false, error: null });
        return result;
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message
            : "Algo salió mal. Intenta de nuevo.";
        setState({ data: null, isLoading: false, error: message });
        return undefined;
      }
    },
    [asyncFn],
  );

  return { ...state, execute };
}