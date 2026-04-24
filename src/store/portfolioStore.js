import { create } from "zustand";
import { persist } from "zustand/middleware";

export const usePortfolioStore = create(
  persist(
    (set) => ({
      prompt: "",
      skills: [],
      preferences: { online: false, location: "" },
      setPrompt: (prompt) => set({ prompt }),
      setSkills: (skills) => set({ skills }),
      setPreferences: (preferences) => set({ preferences }),
      reset: () =>
        set({
          prompt: "",
          skills: [],
          preferences: { online: false, location: "" },
        }),
    }),
    { name: "careermatch-portfolio" }
  )
);
