import { FaSun, FaMoon } from "react-icons/fa";
import useTheme from "../../hooks/useTheme";

const ToggleButtonTheme = () => {
  const [colorTheme, setTheme] = useTheme();
  // const [dark, setDarkSide] = useState(colorTheme === "light" ? true : false);

  const toggleDarkMode = () => {
    setTheme(colorTheme === "light" ? "dark" : "light");
  };

  return (
    <div className="flex items-center gap-1">
      <FaSun className="text-white text-2xl dark:text-black animate-fadeIn duration-200" />
      <input
        type="checkbox"
        className="toggle toggle-warning [--tglbg:white] bg-gray-700  border-black"
        // hover:bg-black
        checked={colorTheme === "dark"}
        onChange={toggleDarkMode}
      />
      <FaMoon className="text-white text-2xl text text-text-light dark:text-white animate-fadeIn duration-200" />
    </div>
  );
};

export default ToggleButtonTheme;
