import { NavBarSection, JumboTron } from "../../components";

const HomePage = () => {
  return (
    <div className="w-full h-dvh bg-white flex flex-col gap-10">
      <div>
        <nav>
          <NavBarSection />
        </nav>
      </div>
      <div className="flex justify-center">
        <JumboTron />
      </div>
    </div>
  );
};

export default HomePage;
