import { ModalClient } from 'modal';

const modal = new ModalClient();
const app = await modal.apps.fromName("meeting-bot", {
  createIfMissing: true,
})
const image = modal.images.fromRegistry("ghcr.io/screenappai/meeting-bot:latest")

const createBaseImage = async () => {
  const sandbox = await modal.sandboxes.create(app, image);
  const p = await sandbox.exec(["git", "clone", "https://github.com/twentysixlabs/healthnotes-meeting-bot"]);
  await p.wait()
  const p2 = await sandbox.exec(["npm run build"]);
  console.log(sandbox.sandboxId)
  await sandbox.snapshotFilesystem();
  sandbox.terminate()
}
``
const createMeetingSandbox = async () => {
  const sandbox = await modal.sandboxes.create(app, image, {
    timeoutMs: 3 * 60 * 60 * 1000 // 3 hours
  });
  const p = await sandbox.exec(["npm run start"]);
  await p.wait()
  console.log(sandbox.sandboxId)
}

createBaseImage().catch(console.error)
// createMeetingSandbox().catch(console.error)