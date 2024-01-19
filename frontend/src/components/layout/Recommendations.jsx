import React from "react";
import RatingRounded from "../roundedComponents/RatingRounded";
import ViewsRounded from "../roundedComponents/ViewsRounded";

const Recommendations = () => {
  return (
    <div className="w-full h-dvh pl-2 ">
      <Card />
    </div>
  );
};

export default Recommendations;

const Card = () => {
  return (
    <div className="w-[30%] bg-red-800 flex gap-1">
      <figure className="w-[40%] flex items-center">
        <img
          src="../../../public/images/th.jpeg"
          alt="Image not found"
          className=""
        />
      </figure>
      <div className="w-[59%] flex flex-col items-center">
        <h1 className="text-left font-Quicksand font-semibold text-white text-2xl">
          Romance and Dummy Book 3
        </h1>
        <p>
          Experience a tale of love and passion as two hearts entwine amidst the
          challenges of life. Can they overcome the obstacles and find true
          happiness?
        </p>
        <div>
          <RatingRounded />
          <ViewsRounded />
        </div>
      </div>
    </div>
  );
};
