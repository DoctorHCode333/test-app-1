import React from 'react';
import {
    Typography,
  } from "@mui/material";
export default function Footer() {
    return(
        <div className='flex flex-row justify-center  bg-gradient-to-tl from-orange-400 via-amber-400 to-orange-400 rounded-2xl py-1 ' style={{width:"98vw",margin:"0px auto"}}>
            {/* <Typography sx={{fontSize: ".9rem",fontWeight:'500',}}>  Version: 1.4.1</Typography> */}
            <Typography sx={{fontSize: ".9rem",fontWeight:'500',}}>  Version: 1.5.1</Typography>
           
        </div>

    )
}

// 