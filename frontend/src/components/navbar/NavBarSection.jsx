import { IoIosSearch } from "react-icons/io";
import { ImCross } from "react-icons/im";
import { useState } from "react";
import ToggleButtonTheme from "../Button/ToggleButtonTheme";
import useTheme from "../../hooks/useTheme";

const NavBarSection = () => {
  const [isHidden, setIsHidden] = useState(false);
  const [theme] = useTheme();

  const toggleVisibility = () => {
    setIsHidden(!isHidden);
  };

  return (
    <div className="w-full h-[67px] dark:bg-black bg-bg-nav box-border flex justify-around ">
      {isHidden === false && (
        <>
          <div className="flex justify-evenly items-center gap-10 animate-fadeIn ">
            <Logo />
          </div>

          <div className="flex items-center animate-fadeIn ">
            <Navbar toggle={toggleVisibility} />
          </div>
        </>
      )}

      {isHidden === true && (
        <div className="flex items-center animate-fadeI dark:animate-fadeIn">
          <ButtonSearch toggleButton={toggleVisibility} />
        </div>
      )}
    </div>
  );
};
export default NavBarSection;

const Logo = () => {
  return (
    <>
      <div className="flex justify-between items-center gap-2">
        <a href="">
          <img
            src="../../public/icons/narrativenet.png"
            alt="Logo"
            className="w-[45px] cursor-pointer"
          />
        </a>
        <p className="text-black dark:text-gray-200 font-Quicksand font-medium text-2xl">
          NarrativeNet
        </p>
      </div>
      <div className="flex ">
        <ul className="flex items-center">
          <li className="items-start">
            <a
              href=""
              className="dark:text-gray-200 text-black font-Quicksand font-normal text-xl relative hover:before:opacity-100 before:absolute before:inset-x-0 before:bottom-0 before:h-[3px] before:bg-black dark:before:bg-white before:opacity-0 before:transition-opacity before:duration-500"
            >
              browse
            </a>
          </li>
        </ul>
      </div>
    </>
  );
};

const Navbar = (props) => {
  return (
    <nav>
      <ul className="flex justify-between items-center gap-10">
        <li>
          <button
            onClick={props.toggle}
            className="btn btn-circle dark:bg-gray-300 active:text-white"
          >
            <IoIosSearch className="size-[30px] dark:text-black hover:text-white active:text-white" />
          </button>
        </li>
        <li>
          <ToggleButtonTheme />
        </li>
      </ul>
    </nav>
  );
};

const ButtonSearch = (props) => {
  return (
    <>
      <button
        onClick={props.toggleButton}
        className="btn btn-square rounded-tr-none rounded-br-none bg-black dark:bg-gray-300 text-2xl border-none text-white dark:text-gray-600"
      >
        <ImCross />
      </button>
      <input
        type="text"
        placeholder="Search"
        className="input w-[500px] max-w-xs rounded-none dark:bg-gray-300"
      />
      <button className="btn btn-square rounded-tl-none rounded-bl-none dark:dark:bg-gray-300 bg-black text-2xl border-none text-white dark:text-gray-600">
        <IoIosSearch />
      </button>
    </>
  );
};
