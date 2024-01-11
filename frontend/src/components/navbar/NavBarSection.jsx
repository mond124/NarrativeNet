import { IoIosSearch } from "react-icons/io";
// import { MdOutlineMenu } from "react-icons/md";

const NavBarSection = () => {
  return (
    <div className="w-full h-[67px] bg-bg-nav box-border flex justify-around">
      <div className="flex justify-evenly items-center gap-10">
        <div className="flex justify-between items-center">
          <a href="">
            <img
              src="../../public/icons/PDI-Perjuangan.svg"
              alt="Logo"
              className="w-[80px] cursor-pointer"
            />
          </a>
          <p className="text-black font-Quicksand font-medium text-2xl">
            NarrativeNet
          </p>
        </div>
        <div className="flex ">
          <ul className="flex items-center">
            <li className="items-start">
              <a
                href=""
                className="text-black font-Quicksand font-normal text-xl relative hover:before:opacity-100 before:absolute before:inset-x-0 before:bottom-0 before:h-[3px] before:bg-black before:opacity-0 before:transition-opacity before:duration-500"
              >
                browse
              </a>
            </li>
          </ul>
        </div>
        {/* <details className="dropdown">
          <summary tabIndex={0} className="m-1 btn">
            <MdOutlineMenu />
          </summary>
          <ul
            tabIndex={0}
            className="p-2 shadow menu dropdown-content z-[1] bg-base-100 rounded-box w-52"
          >
            <li>
              <a>Item 1</a>
            </li>
            <li>
              <a>Item 2</a>
            </li>
          </ul>
        </details> */}
      </div>

      <div className="flex items-center">
        <nav>
          <ul className="flex justify-between items-center gap-6">
            <li>
              <button className="btn btn-circle bg-gray-300 active:text-white">
                <IoIosSearch className="size-[30px] text-black hover:text-white active:text-white" />
              </button>
            </li>
            <li>
              <input
                type="checkbox"
                className="toggle toggle-warning [--tglbg:white] bg-gray-700  border-black"
                // hover:bg-black
              />
            </li>
          </ul>
        </nav>
      </div>
    </div>
  );
};

export default NavBarSection;
