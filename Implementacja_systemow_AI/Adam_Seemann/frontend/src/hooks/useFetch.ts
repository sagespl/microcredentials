import { useEffect, useState } from "react";

interface FetchState<T> { data: T | null; error: Error | null; loading: boolean; }

export function useFetch<T>(request: (signal: AbortSignal) => Promise<T>, dependencies: unknown[]) {
  const [state, setState] = useState<FetchState<T>>({ data: null, error: null, loading: true });

  useEffect(() => {
    const controller = new AbortController();
    setState({ data: null, error: null, loading: true });
    request(controller.signal)
      .then((data) => setState({ data, error: null, loading: false }))
      .catch((error: Error) => {
        if (error.name !== "AbortError") setState({ data: null, error, loading: false });
      });
    return () => controller.abort();
  }, dependencies); // Dependencies describe when the caller wants a new request.

  return state;
}