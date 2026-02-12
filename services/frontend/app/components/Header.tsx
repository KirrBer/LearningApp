'use client'

import Link from "next/link";
import Image from "next/image";
import menu from '@/app/assets/menu.png'
import { useState, useEffect } from "react";

export const Header = () => {
    const [isOpenedMenu, setIsOpenedMenu] = useState<boolean>(false)

    const handleClick = () =>{
        setIsOpenedMenu((prevState) => (!prevState))
    }


    return <header className="w-full h-14 xl:h-20 z-[100] fixed top-0 left-0 bg-white">
        <div className="w-full h-full max-w-screen-2xl mx-auto flex items-center justify-between px-2.5">
            <Link href="/" className="flex items-center h-full shrink-0">
                <span className="ml-2 text-base xl:text-2xl font-bold text-black">LearningApp</span>
            </Link>
            <nav className="w-fit h-full flex gap-2 lg:gap-6 font-medium text-base lg:text-xl items-center leading-none">
                <Link href={"/"} className="hidden lg:block hover:text-blue-600 transition-colors">Главная</Link>
                <Link href={"/courses"} className="hidden lg:block hover:text-blue-600 transition-colors">База курсов</Link>
                <Link href={"/jobs"} className="hidden lg:block hover:text-blue-600 transition-colors">Вакансии</Link>
                <Link href={"/learning_path_generator"} className="hidden lg:block hover:text-blue-600 transition-colors">Генератор путей</Link>
                <Link href={"/skill_analyzer"} className="hidden lg:block hover:text-blue-600 transition-colors">Анализ скилов</Link>
                <Link href={"/profile"} className="hidden lg:block hover:text-blue-600 transition-colors">Профиль</Link>
                <Image onClick={handleClick} src={menu} alt='menu' width={40} height={40} className="block lg:hidden h-10 w-10 cursor-pointer"></Image>
                {
                isOpenedMenu && <div className="bg-gray-300 w-1/2 h-fit min-h-[50vh] fixed top-14 right-0 flex flex-col text-xl items-left gap-7 pl-8 pt-4">
                    <Link href={"/"} className="hidden lg:block hover:text-blue-600 transition-colors">Главная</Link>
                    <Link href={"/courses"} className="hover:text-blue-600 transition-colors">База курсов</Link>
                    <Link href={"/jobs"} className="hover:text-blue-600 transition-colors">Вакансии</Link>
                    <Link href={"/learning_path_generator"} className="lg:block hover:text-blue-600 transition-colors">Генератор путей</Link>
                    <Link href={"/skills_analyzer"} className="lg:block hover:text-blue-600 transition-colors">Анализ скилов</Link>
                    <Link href={"/profile"} className="lg:block hover:text-blue-600 transition-colors">Профиль</Link>
                </div>
                }
            </nav>
        </div>
    </header>
}