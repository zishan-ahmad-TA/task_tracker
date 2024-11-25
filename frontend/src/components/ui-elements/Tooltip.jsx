import * as Tooltip from "@radix-ui/react-tooltip";
import styles from "./Tooltip.module.css";

const TooltipComponent = ({ children, tooltipText }) => {
    return (
        <Tooltip.Provider>
            <Tooltip.Root>
                <Tooltip.Trigger asChild>
                    <div>
                        {children}
                    </div>
                </Tooltip.Trigger>
                <Tooltip.Portal>
                    <Tooltip.Content className={styles.Content} sideOffset={5}>
                        {tooltipText}
                        <Tooltip.Arrow className={styles.Arrow} />
                    </Tooltip.Content>
                </Tooltip.Portal>
            </Tooltip.Root>
        </Tooltip.Provider>
    );
};

export default TooltipComponent;
