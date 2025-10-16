import Head from "next/head";
import Navbar from "./Navbar";
import React, { ReactNode } from "react";
import SocialIcons from "./SocialIcons";

interface Props {
  children: ReactNode;
}

const Layout = ({ children }: Props) => {
  return (
    <>
      <Head>
        <title>AiGov AI Assistant</title>
        <meta property="og:title" content="AiGov AI Assistant" key="title" />
      </Head>
      <div className="min-h-screen">
        {children}
      </div>
    </>
  );
};
export default Layout;
