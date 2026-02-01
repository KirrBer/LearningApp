import Link from "next/link";

export const Footer = () => {
    return (
        <footer className="w-full flex flex-col bg-neutral-900 text-neutral-200 py-6 xl:py-12">
            <div className="w-full max-w-screen-2xl mx-auto flex flex-row items-start md:items-center justify-between px-4 xl:px-8 gap-y-6 md:gap-y-0">
                <div className="flex flex-col gap-y-3 xl:gap-y-5 font-medium text-[16px] xl:text-[18px] leading-none">
                    <Link href={"/"} className="hover:text-red-200 transition-colors">Главная</Link>
                    <Link href={"/courses"} className="hover:text-red-200 transition-colors">Курсы</Link>
                    <Link href={"/about"} className="hover:text-red-200 transition-colors">О нас</Link>
                </div>
                <div className="flex flex-col gap-y-3 xl:gap-y-5 font-medium text-[16px] xl:text-[18px] leading-none">
                    <Link href={"/login"} className="hover:text-red-200 transition-colors">Войти</Link>
                    <Link href={"/registration"} className="hover:text-red-200 transition-colors">Регистрация</Link>
                </div>
                <div className="text-sm text-neutral-400">
                    <p>Свяжитесь с нами:</p>
                    <p>some@email.com</p>
                    <p>+7 (000) 000-00-00</p>
                </div>
            </div>

            <div className="w-full max-w-screen-2xl mx-auto flex font-medium text-[12px] xl:text-[16px] text-neutral-500 items-center justify-between px-4 xl:px-8 mt-6 xl:mt-12 pt-6 border-t border-neutral-700">
                <span>© 2025, LearningApp. Все права защищены.</span>
            </div>
        </footer>
    );
};