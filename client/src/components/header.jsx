import React from 'react';
import Logo from './logo'
import HeaderNav from './headerNav'
import SignIn from './sign-in'
import UtilityComponent from "./utilityHeaderComponent";

const Header = (props) => {
    const customHeaderStyle = {
        zIndex: "10",
    };

    return (
        <div className="m-auto d-flex align-items-center justify-content-center " style={customHeaderStyle}>
            <UtilityComponent tags={props.utilityTags}/>
            <header className="shadow-lg d-flex align-items-center justify-content-center">
                <Logo onClick={props.onClick}/>
            </header>
            {/* ================== */}
            <header className="shadow-lg d-flex align-items-center justify-content-center">
                <HeaderNav onClick={props.onClick}/>
            </header>
            {/* ================== */}
            <header className="shadow-lg d-flex align-items-center justify-content-center">
                <SignIn onClick={props.onClick}/>
            </header>
        </div>
    );
};

export default Header;