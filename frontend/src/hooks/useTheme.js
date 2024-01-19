import { useState, useEffect } from "react";

export default function useTheme() {
  const storedTheme = localStorage.getItem('theme');
  const initialTheme = storedTheme || 'light';

  const [theme, setTheme] = useState(initialTheme);
  const colorTheme = theme === 'dark' ? 'dark' : 'light';

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove(colorTheme === 'dark' ? 'light' : 'dark');
    root.classList.add(theme);

    localStorage.setItem('theme', theme);
  }, [theme, colorTheme]);

  return [colorTheme, setTheme];
}
