import * as Dialog from "@radix-ui/react-dialog";
import styles from "./Dialog.module.css";
import { RxCross1 } from "react-icons/rx";

const DialogComponent = ({
    open,
    onOpenChange,
    title,
    buttonText,
    buttonColor,
    onSubmit,
    children
}) => (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
        <Dialog.Portal>
            <Dialog.Overlay className={styles.Overlay} />
            <Dialog.Content className={styles.Content}>
                <Dialog.Title className={styles.Title}>{title}</Dialog.Title>
                {children}
                <div
                    style={{ display: "flex", marginTop: 25, justifyContent: "flex-end" }}
                >
                    <Dialog.Close asChild>
                        <button
                            className={`${styles.Button}`}
                            style={{ background: buttonColor }}
                            onClick={() => {
                                onSubmit();
                                onOpenChange(false);
                            }}
                        >
                            {buttonText}
                        </button>
                    </Dialog.Close>
                </div>
                <Dialog.Close asChild>
                    <button className={styles.IconButton} aria-label="Close">
                        <RxCross1 />
                    </button>
                </Dialog.Close>
            </Dialog.Content>
        </Dialog.Portal>
    </Dialog.Root>
);

export default DialogComponent;
