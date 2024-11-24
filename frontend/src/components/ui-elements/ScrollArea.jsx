import * as ScrollArea from "@radix-ui/react-scroll-area";
import styles from './ScrollArea.module.css';


const ScrollAreaDemo = ({ dataCard }) => (
    <ScrollArea.Root className={styles.ScrollAreaRoot}>
        <ScrollArea.Viewport className={styles.ScrollAreaViewport}>
            <div style={{ padding: "15px 20px" }}>
                <div className="Text">Tags</div>
                {dataCard.map((tag) => (
                    <div className="Tag" key={tag}>
                        {tag}
                    </div>
                ))}
            </div>
        </ScrollArea.Viewport>
        <ScrollArea.Scrollbar
            className={styles.ScrollAreaScrollbar}
            orientation="vertical"
        >
            <ScrollArea.Thumb className={styles.ScrollAreaThumb} />
        </ScrollArea.Scrollbar>
        <ScrollArea.Scrollbar
            className={styles.ScrollAreaScrollbar}
            orientation="horizontal"
        >
            <ScrollArea.Thumb className={styles.ScrollAreaThumb} />
        </ScrollArea.Scrollbar>
        <ScrollArea.Corner className={styles.ScrollAreaCorner} />
    </ScrollArea.Root>
);

export default ScrollAreaDemo;
