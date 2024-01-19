import { FaSun, FaMoon } from "react-icons/fa";
import useTheme from "../../hooks/useTheme";
import { color } from "framer-motion";

const ToggleButtonTheme = () => {
  const [colorTheme, setTheme] = useTheme();
  // const [dark, setDarkSide] = useState(colorTheme === "light" ? true : false);

  const toggleDarkMode = () => {
    setTheme(colorTheme === "light" ? "dark" : "light");
  };

  return (
    <div className="flex items-center gap-1">
      {colorTheme === "light" && (
        <FaSun className="text-white text-2xl animate-fadeIn duration-200" />
      )}
      <input
        type="checkbox"
        className="toggle toggle-warning [--tglbg:white] bg-gray-700  border-black"
        // hover:bg-black
        checked={colorTheme === "dark"}
        onChange={toggleDarkMode}
      />
      {colorTheme === "dark" && (
        <FaMoon className="text-white text-2xl text animate-fadeIn duration-200" />
      )}
    </div>
  );
};

export default ToggleButtonTheme;
