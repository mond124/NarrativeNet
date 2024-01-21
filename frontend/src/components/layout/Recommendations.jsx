import React, { useState } from "react";
import RatingRounded from "../roundedComponents/RatingRounded";
import ViewsRounded from "../roundedComponents/ViewsRounded";
import { FaArrowRight } from "react-icons/fa6";
import GenreRounded from "../roundedComponents/GenreRounded";

const Recommendations = () => {
  let synopsis =
    "Experience a tale of love and passion as two hearts entwine amidst the challenges of life. Can they overcome the obstacles and find true happiness?";

  return (
    <div className="w-full h-dvh pl-2 flex gap-1 flex-col">
      <p className="flex items-center gap-1 justify-end pr-5 text-black font-Quicksand font-semibold text-xl">
        <a href="">More</a>
        <FaArrowRight />
      </p>

      <h1 className="text-black font-Quicksand font-bold text-2xl text-center">
        Recomendation
      </h1>
      <div className="w-[full] flex flex-wrap  gap-1 justify-center">
        <Card synopsis={synopsis} />
        <Card synopsis={synopsis} />
        <Card synopsis={synopsis} />
        <Card synopsis={synopsis} />
        <Card synopsis={synopsis} />
        <Card synopsis={synopsis} />
        <Card synopsis={synopsis} />
        <Card synopsis={synopsis} />
        <Card synopsis={synopsis} />
      </div>
    </div>
  );
};

export default Recommendations;

const Card = (props) => {
  const [expanded, setExpanded] = useState(false);

  const toggleExpand = () => {
    setExpanded(!expanded);
  };

  return (
    <div
      className={`w-[27%] flex gap-2 dark:border-solid border-2 dark:bg-gray-700 border-none bg-white border-black rounded-md shadow-xl ${
        expanded ? "h-auto" : "min-h-[200px] overflow-hidden"
      }`}
    >
      <figure className="w-[40%] flex items-center">
        <img
          src="../../../public/images/th.jpeg"
          alt="Image not found"
          className=""
        />
      </figure>
      <div className="w-[59%] flex flex-col items-center gap-2">
        <h1 className="text-center font-Quicksand font-semibold dark:text-white text-black text-2xl">
          Romance and Dummy Book 3
        </h1>
        <GenreRounded />

        {WordCount(props.synopsis) >= 8 ? (
          <div className="flex flex-wrap">
            <p className="dark:text-white text-black text-sm">
              {expanded
                ? props.synopsis
                : props.synopsis
                    .split(" ")
                    .slice(0, 10)
                    .join(" ")
                    .concat("", "...", " ")}
            </p>
            <button
              onClick={toggleExpand}
              className="text-blue-500 cursor-pointer"
            >
              {expanded ? "Read Less" : "Read More"}
            </button>
          </div>
        ) : (
          <p>{props.synopsis}</p>
        )}
        <div className="flex gap-5">
          <RatingRounded />
          <ViewsRounded />
        </div>
      </div>
    </div>
  );
};

function WordCount(synopsis) {
  return synopsis.split(" ").length;
}
