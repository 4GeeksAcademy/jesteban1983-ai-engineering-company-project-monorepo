// components/AsyncView.tsx — Renderiza automáticamente: cargando, error, datos o vacío
//
// Props:
//   isLoading  — true mientras se carga
//   error      — string de error o null
//   data       — datos tipados o null
//   onRetry    — callback para reintentar (opcional)
//   loadingMessage — mensaje personalizado de carga
//   children   — renderiza con datos tipados
//
// Uso:
//   <AsyncView isLoading error data={users} onRetry={execute}>
//     {(users) => <UserList users={users} />}
//   </AsyncView>

"use client";

import React from "react";

interface AsyncViewProps<T> {
  isLoading: boolean;
  error: string | null;
  data: T | null;
  onRetry?: () => void;
  loadingMessage?: string;
  children: (data: T) => React.ReactNode;
}

export function AsyncView<T>({
  isLoading,
  error,
  data,
  onRetry,
  loadingMessage = "Cargando...",
  children,
}: AsyncViewProps<T>) {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
        <p className="text-sm text-gray-500">{loadingMessage}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
        <p className="mb-2 font-medium text-red-800">Algo salió mal</p>
        <p className="mb-4 text-sm text-red-600">{error}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="rounded bg-red-600 px-4 py-2 text-sm text-white transition hover:bg-red-700"
          >
            Intentar de nuevo
          </button>
        )}
        <a
          href="/"
          className="mt-2 block text-sm text-blue-600 underline hover:text-blue-800"
        >
          Volver al inicio
        </a>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-8 text-center text-gray-400">
        No hay datos disponibles.
      </div>
    );
  }

  return <>{children(data)}</>;
}