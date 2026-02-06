import { useEffect, useState } from "react";
import ProtocolItems from "./screens/ProtocolItems";
import Protocols from "./screens/Protocols";

export type Screen = { name: "protocols" } | { name: "items"; protocolId: number };

export default function App() {
  const [screen, setScreen] = useState<Screen>({ name: "protocols" });

  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    if (tg) {
      tg.ready();
      tg.expand();
    }
  }, []);

  if (screen.name === "items") {
    return <ProtocolItems protocolId={screen.protocolId} onBack={() => setScreen({ name: "protocols" })} />;
  }

  return <Protocols onOpen={(id) => setScreen({ name: "items", protocolId: id })} />;
}
