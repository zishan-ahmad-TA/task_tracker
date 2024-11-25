import * as Dialog from "@radix-ui/react-dialog";
import styles from "./Dialog.module.css";
import { RxCross1 } from "react-icons/rx";

const DialogComponent = ({
    title,
    description,
    fields = [],
    buttonText,
    onSave,
}) => (
    <Dialog.Root>
        <Dialog.Trigger asChild>
        </Dialog.Trigger>
        <Dialog.Portal>
            <Dialog.Overlay className={styles.Overlay} />
            <Dialog.Content className={styles.Content}>
                <Dialog.Title className={styles.Title}>{title}</Dialog.Title>
                <Dialog.Description className={styles.Description}>
                    {description}
                </Dialog.Description>
                {fields.map((field, index) => (
                    <fieldset key={index} className={styles.Fieldset}>
                        <label className={styles.Label} htmlFor={field.id}>
                            {field.label}
                        </label>
                        <input
                            className={styles.Input}
                            id={field.id}
                            defaultValue={field.defaultValue}
                        />
                    </fieldset>
                ))}
                <div
                    style={{ display: "flex", marginTop: 25, justifyContent: "flex-end" }}
                >
                    <Dialog.Close asChild>
                        <button className={`${styles.Button} green`} onClick={onSave}>
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
