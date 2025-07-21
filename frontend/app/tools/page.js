"use client"
import SideBar from '@/components/tools/SideBar'
import ImageSumary from '@/components/tools/ImageSumary';
import ImageCaption from '@/components/tools/ImageCaption';
import {useState} from 'react';

export default function page() {
    const [tab, setTab] = useState('image-summary');
    return (
        <>
            <SideBar tab={tab} setTab={setTab}>
                {tab === 'image-summary' && <ImageSumary />}
                {/* {tab === 'image-caption' && <ImageCaption />} */}
            </SideBar>
        </>
    )
}
