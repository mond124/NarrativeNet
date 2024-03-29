import { NavBarSection, JumboTron, Recommendations } from "../../components";

const HomePage = () => {
  return (
    <div className="w-full h-full bg-white flex flex-col gap-20">
      <div className="flex flex-col">
        <div>
          <nav className="relative">
            <NavBarSection />
          </nav>
        </div>
        <div className="flex justify-center ">
          <JumboTron />
        </div>
      </div>
      <div className="bg-white">
        <Recommendations />
      </div>
    </div>
  );
};

export default HomePage;
