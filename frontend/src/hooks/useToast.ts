import { create } from 'zustand';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastMessage {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastState {
  toasts: ToastMessage[];
  showToast: (message: string, type: ToastType) => void;
  dismissToast: (id: string) => void;
}

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],
  showToast: (message, type) => {
    const id = Math.random().toString(36).substring(2, 9);
    set((state) => {
      const newToasts = [...state.toasts, { id, message, type }];
      if (newToasts.length > 3) {
        newToasts.shift();
      }
      return { toasts: newToasts };
    });

    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter((t) => t.id !== id),
      }));
    }, 4000);
  },
  dismissToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));

export const useToast = () => {
  const showToast = useToastStore((state) => state.showToast);
  return { showToast };
};
