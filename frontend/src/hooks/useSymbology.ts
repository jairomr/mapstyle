import { useState, useCallback, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from '../api/symbology';
import {
  SymbologyCreate,
  SymbologyResponse,
  ConfigResponse,
  FormState,
} from '../types/symbology';
import { DEFAULT_FORM_STATE } from '../utils/constants';

interface UseSymbologyOptions {
  urlKey?: string;
  onSuccess?: (response: SymbologyResponse) => void;
  onError?: (error: Error) => void;
}

/**
 * Custom hook para gerenciar estado e operações de simbologia
 */
export function useSymbology({
  urlKey,
  onSuccess,
  onError,
}: UseSymbologyOptions = {}) {
  // Estado do formulário
  const [formState, setFormState] = useState<FormState>(DEFAULT_FORM_STATE);
  const [currentUrlKey, setCurrentUrlKey] = useState<string | null>(urlKey || null);

  // Query para carregar simbologia existente
  const {
    data: existingConfig,
    isLoading: isLoadingConfig,
    error: configError,
  } = useQuery<ConfigResponse>({
    queryKey: ['symbology', currentUrlKey],
    queryFn: () => api.getSymbologyConfig(currentUrlKey!),
    enabled: !!currentUrlKey,
  });

  // Atualizar form quando config é carregada
  useEffect(() => {
    if (existingConfig?.symbology) {
      setFormState(existingConfig.symbology);
    }
  }, [existingConfig]);

  // Mutation para criar simbologia
  const createMutation = useMutation({
    mutationFn: (data: SymbologyCreate) => api.createSymbology(data),
    onSuccess: (response) => {
      // Só guardar a url_key, o formulário já tem os valores do usuário
      setCurrentUrlKey(response.url_key);
      onSuccess?.(response);
    },
    onError: (error) => {
      onError?.(error as Error);
    },
  });

  // Handlers de formulário
  const updateFormField = useCallback(
    <K extends keyof FormState>(field: K, value: FormState[K]) => {
      setFormState((prev) => ({ ...prev, [field]: value }));
    },
    []
  );

  const updateForm = useCallback((updates: Partial<FormState>) => {
    setFormState((prev) => ({ ...prev, ...updates }));
  }, []);

  const resetForm = useCallback(() => {
    setFormState(DEFAULT_FORM_STATE);
    setCurrentUrlKey(null);
  }, []);

  const createSymbology = useCallback(async () => {
    return createMutation.mutateAsync(formState);
  }, [formState, createMutation]);

  const loadFromUrlKey = useCallback((key: string) => {
    setCurrentUrlKey(key);
  }, []);

  // Auto-submit com debounce quando formState muda
  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentUrlKey) {
        // Só auto-submete se já tem um url_key gerado
        createMutation.mutateAsync(formState);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [formState, currentUrlKey]);

  return {
    // State
    formState,
    currentUrlKey,
    existingConfig,
    isLoading: isLoadingConfig || createMutation.isPending,
    error: configError || createMutation.error,

    // Actions
    updateFormField,
    updateForm,
    resetForm,
    createSymbology,
    loadFromUrlKey,
  };
}
