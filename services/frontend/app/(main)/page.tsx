import mainImage from '@/app/assets/main.jpeg';
import Link from "next/link";
import Image from "next/image";

export default function MainPage() {
    return(
        <div className='inline-block w-full h-[50vh] object-cover relative'>
            <Image src={mainImage} alt='programming' width={2560} height={1707} className='w-full h-[50vh] object-cover flex items-center justify-center'></Image>
            <Link href={"/login"} className='absolute top-1/3 inset-x-1/3 bg-gray-200 p-3 text-sm lg:text-xl font-bold hover:bg-gray-400 flex justify-center'>Войти</Link>
            <Link href={"/registration"} className='absolute top-3/5 inset-x-1/3 bg-gray-200 p-3 text-sm lg:text-xl font-bold hover:bg-gray-400 flex justify-center'>Зарегистрироваться</Link>
        </div>
    );
}