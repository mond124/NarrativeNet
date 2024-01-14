import { NavBarSection, JumboTron } from "../../components";

const HomePage = () => {
  return (
    <div className="w-full h-dvh bg-white flex flex-col gap-5">
      <div>
        <nav className="relative">
          <NavBarSection />
        </nav>
      </div>
      <div className="flex justify-center gap-2">
        <JumboTron />
      </div>
      <div className="flex justify-center gap-2">
        <JumboTron />
      </div>
      <div className="flex justify-center gap-2">
        <JumboTron />
      </div>
      <div className="flex justify-center gap-2">
        <JumboTron />
      </div>
      <div className="flex justify-center gap-2">
        <JumboTron />
      </div>
      <div className="flex justify-center gap-2">
        <JumboTron />
      </div>
    </div>
  );
};

export default HomePage;
