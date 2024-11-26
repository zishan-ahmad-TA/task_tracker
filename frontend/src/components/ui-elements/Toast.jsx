import * as Toast from "@radix-ui/react-toast";
import styles from "./Toast.module.css";

const ToastComponent = ({
  open,
  setOpen,
  toastTitle = "Notification",
  toastMessage = "Something happened!",
  buttonActionText = null,
  onActionClick = null,
}) => {
  return (
    <Toast.Provider swipeDirection="right">
      <Toast.Root className={styles.Root} open={open} onOpenChange={setOpen}>
        <Toast.Title className={styles.Title}>{toastTitle}</Toast.Title>
        <Toast.Description className={styles.Description}>
          {toastMessage}
        </Toast.Description>

        {buttonActionText && onActionClick && (
          <Toast.Action
            className={styles.Action}
            asChild
            altText="Action button"
          >
            <button
              className={`${styles.Button} small green`}
              onClick={onActionClick}
            >
              {buttonActionText}
            </button>
          </Toast.Action>
        )}
      </Toast.Root>
      <Toast.Viewport className={styles.Viewport} />
    </Toast.Provider>
  );
};

export default ToastComponent;
