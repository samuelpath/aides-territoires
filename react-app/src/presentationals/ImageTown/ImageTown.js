import React from "react";

const url = "/static/images/flat-design-town.png";

const size = "400px";
const borderRadius = size;
const style = {
  background: `url("${url}")`,
  backgroundSize: "100%",
  backgroundPosition: "center",
  height: 100
};

export default class extends React.Component {
  render() {
    // return <div style={style} className="image-town" />;
    return <img src={url} className="image-town" />;
  }
}