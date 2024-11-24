import React from "react";
import * as HoverCard from "@radix-ui/react-hover-card";
import styles from "./HoverCard.module.css";
import AvatarComponent from "./Avatar";
import { getInitials } from "../../utils/getInitials";

const HoverCardComponent = ({ profileImage, name, email, role }) => (
    <HoverCard.Root>
        <HoverCard.Trigger asChild>
            <div>
                <AvatarComponent src={profileImage} alt={`${name}-profile`} fallback={getInitials(name)} />
            </div>
        </HoverCard.Trigger>
        <HoverCard.Portal>
            <HoverCard.Content className={styles.HoverCardContent} sideOffset={5}>
                <div>
                    <div className={`${styles.Text} ${styles.bold}`}>{role}</div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 15 }}>
                        <div>
                            <div className={`${styles.Text} ${styles.bold}`}>{name}</div>
                            <div className={`${styles.Text} ${styles.faded}`}>{email}</div>
                        </div>
                    </div>
                </div>

                <HoverCard.Arrow className={styles.HoverCardArrow} />
            </HoverCard.Content>
        </HoverCard.Portal>
    </HoverCard.Root>
);

export default HoverCardComponent;
