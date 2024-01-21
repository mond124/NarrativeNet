import { IoIosSearch } from "react-icons/io";
import { ImCross } from "react-icons/im";
import { useState, useEffect } from "react";
import ToggleButtonTheme from "../Button/ToggleButtonTheme";
import useTheme from "../../hooks/useTheme";
import Typed from "react-typed";

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
        <p className="text-white dark:text-white font-Quicksand font-medium text-2xl">
          <Typed
            strings={["NarrativeNet", "Manga", "Novel"]}
            typeSpeed={40}
            backSpeed={50}
            loop
          ></Typed>
        </p>
      </div>
      <div className="flex ">
        <ul className="flex items-center">
          <li className="items-start">
            <a
              href=""
              className="dark:text-white text-white font-Quicksand font-normal text-xl relative hover:before:opacity-100 before:absolute before:inset-x-0 before:bottom-0 before:h-[3px] before:bg-black dark:before:bg-white before:opacity-0 before:transition-opacity before:duration-500"
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
            className="btn btn-circle dark:bg-gray-800 bg-bg-nav border-none active:text-white"
          >
            <IoIosSearch className="size-[30px] text-white hover:text-white active:text-white" />
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
        className="btn btn-square rounded-tr-none rounded-br-none bg-black dark:bg-gray-800 text-2xl border-none text-white dark:text-white"
      >
        <ImCross />
      </button>
      <input
        type="text"
        placeholder={props.placeholder}
        className="input w-[500px] max-w-xs rounded-none border-none focus:outline-none dark:bg-gray-800"
      />
      <button className="btn btn-square rounded-tl-none rounded-bl-none dark:dark:bg-gray-800 bg-black text-2xl border-none text-white dark:text-white">
        <IoIosSearch />
      </button>
    </>
  );
};

// * main
const NavBarSection = () => {
  const [isHidden, setIsHidden] = useState(false);

  const [theme] = useTheme();

  const toggleVisibility = () => {
    setIsHidden(!isHidden);
  };

  return (
    <div className="w-full h-[67px] dark:bg-gray-800 bg-bg-nav box-border flex justify-around ">
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
          <ButtonSearch toggleButton={toggleVisibility} placeholder="Search" />
        </div>
      )}
    </div>
  );
};
export default NavBarSection;
