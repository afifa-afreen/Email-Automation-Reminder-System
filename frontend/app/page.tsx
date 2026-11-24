
"use client";

import { useCallback, useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

type Item = {
  id?: number | string;
  name?: string;
  title?: string;
  email?: string;
  company?: string;
  subject?: string;
  status?: string;
  scheduled_at?: string;
  [key: string]: unknown;
};

async function apiRequest(path: string, options: RequestInit = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail
        ? typeof data.detail === "string"
          ? data.detail
          : JSON.stringify(data.detail)
        : `Request failed: ${response.status}`
    );
  }

  return data;
}

function getList(data: unknown): Item[] {
  if (Array.isArray(data)) return data as Item[];

  if (data && typeof data === "object") {
    const obj = data as Record<string, unknown>;
    for (const key of ["items", "data", "results", "contacts", "templates", "campaigns", "reminders", "messages"]) {
      if (Array.isArray(obj[key])) return obj[key] as Item[];
    }
  }

  return [];
}

export default function Home() {
  const [contacts, setContacts] = useState<Item[]>([]);
  const [templates, setTemplates] = useState<Item[]>([]);
  const [campaigns, setCampaigns] = useState<Item[]>([]);
  const [reminders, setReminders] = useState<Item[]>([]);
  const [messages, setMessages] = useState<Item[]>([]);

  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [company, setCompany] = useState("");

  const [templateName, setTemplateName] = useState("welcome");
  const [subject, setSubject] = useState("Hello from our automation system");
  const [html, setHtml] = useState(
    "<h2>Hello {{ name }}</h2><p>Your reminder is ready.</p>"
  );

  const [campaignName, setCampaignName] = useState("Welcome campaign");
  const [campaignTemplateId, setCampaignTemplateId] = useState("");

  const [reminderTitle, setReminderTitle] = useState("Follow-up reminder");
  const [contactId, setContactId] = useState("");
  const [templateId, setTemplateId] = useState("");
  const [scheduled, setScheduled] = useState("");

  const [loading, setLoading] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("overview");
  const [backendStatus, setBackendStatus] = useState("Checking...");

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const results = await Promise.all([
        apiRequest("/contacts"),
        apiRequest("/templates"),
        apiRequest("/campaigns"),
        apiRequest("/reminders"),
        apiRequest("/messages"),
      ]);

      setContacts(getList(results[0]));
      setTemplates(getList(results[1]));
      setCampaigns(getList(results[2]));
      setReminders(getList(results[3]));
      setMessages(getList(results[4]));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load dashboard.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    apiRequest("/health")
      .then(() => setBackendStatus("Connected"))
      .catch(() => setBackendStatus("Disconnected"));

    loadDashboard();
  }, [loadDashboard]);

  async function handleAction(action: () => Promise<unknown>, success: string) {
    setNotice("");
    setError("");

    try {
      await action();
      setNotice(success);
      await loadDashboard();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    }
  }

  async function createContact(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    await handleAction(
      () =>
        apiRequest("/contacts", {
          method: "POST",
          body: JSON.stringify({
            name: contactName,
            email: contactEmail,
            company: company,
          }),
        }),
      "Contact created successfully!"
    );

    setContactName("");
    setContactEmail("");
    setCompany("");
  }

  async function createTemplate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    await handleAction(
      () =>
        apiRequest("/templates", {
          method: "POST",
          body: JSON.stringify({
            name: templateName,
            subject: subject,
            html: html,
          }),
        }),
      "Email template created successfully!"
    );
  }

  async function createCampaign(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    await handleAction(
      () =>
        apiRequest("/campaigns", {
          method: "POST",
          body: JSON.stringify({
            name: campaignName,
            template_id: Number(campaignTemplateId),
          }),
        }),
      "Campaign created successfully!"
    );
  }

  async function sendCampaign(id: number | string | undefined) {
    if (!id) {
      setError("Campaign ID is missing.");
      return;
    }

    if (!window.confirm("Are you sure you want to send this campaign?")) return;

    await handleAction(
      () =>
        apiRequest(`/campaigns/${id}/send-all`, {
          method: "POST",
        }),
      "Campaign send request completed."
    );
  }

  async function createReminder(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    if (!scheduled) {
      setError("Please select a reminder date and time.");
      return;
    }

    await handleAction(
      () =>
        apiRequest("/reminders", {
          method: "POST",
          body: JSON.stringify({
            title: reminderTitle,
            contact_id: Number(contactId),
            template_id: Number(templateId),
            scheduled_at: new Date(scheduled).toISOString(),
          }),
        }),
      "Reminder scheduled successfully!"
    );
  }

  const stats = [
    { label: "Contacts", value: contacts.length, icon: "👥" },
    { label: "Templates", value: templates.length, icon: "📄" },
    { label: "Campaigns", value: campaigns.length, icon: "📢" },
    { label: "Reminders", value: reminders.length, icon: "⏰" },
  ];

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "contacts", label: "Contacts" },
    { id: "templates", label: "Templates" },
    { id: "campaigns", label: "Campaigns" },
    { id: "reminders", label: "Reminders" },
    { id: "messages", label: "Messages" },
  ];

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="flex min-h-screen">
        <aside className="hidden w-64 shrink-0 border-r border-slate-800 bg-slate-900 p-6 md:block">
          <h1 className="text-xl font-bold text-white">
            ✉️ MailFlow
          </h1>
          <p className="mt-2 text-xs text-slate-400">
            Email Automation System
          </p>

          <nav className="mt-10 space-y-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full rounded-lg px-4 py-3 text-left text-sm ${
                  activeTab === tab.id
                    ? "bg-blue-600 text-white"
                    : "text-slate-300 hover:bg-slate-800"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          <div className="mt-10 rounded-lg bg-slate-800 p-4">
            <p className="text-xs text-slate-400">Backend status</p>
            <p className={`mt-2 text-sm font-semibold ${
              backendStatus === "Connected" ? "text-green-400" : "text-yellow-400"
            }`}>
              ● {backendStatus}
            </p>
          </div>
        </aside>

        <section className="min-w-0 flex-1 p-5 md:p-8">
          <header className="mb-8 flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold">
                Email Automation Dashboard
              </h2>
              <p className="mt-1 text-sm text-slate-400">
                Manage contacts, campaigns and automated reminders.
              </p>
            </div>

            <button
              onClick={loadDashboard}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium hover:bg-blue-500"
            >
              ↻ Refresh
            </button>
          </header>

          <div className="mb-6 flex gap-2 overflow-x-auto md:hidden">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`whitespace-nowrap rounded-lg px-3 py-2 text-sm ${
                  activeTab === tab.id ? "bg-blue-600" : "bg-slate-800"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {notice && (
            <div className="mb-5 rounded-lg border border-green-700 bg-green-950 p-3 text-sm text-green-300">
              {notice}
            </div>
          )}

          {error && (
            <div className="mb-5 rounded-lg border border-red-700 bg-red-950 p-3 text-sm text-red-300">
              {error}
            </div>
          )}

          {activeTab === "overview" && (
            <>
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {stats.map((stat) => (
                  <div key={stat.label} className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                    <p className="text-sm text-slate-400">{stat.label}</p>
                    <div className="mt-3 flex items-center justify-between">
                      <p className="text-3xl font-bold">{stat.value}</p>
                      <span className="text-3xl">{stat.icon}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 grid gap-6 xl:grid-cols-2">
                <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                  <h3 className="mb-4 text-lg font-semibold">Recent reminders</h3>
                  {reminders.length === 0 ? (
                    <p className="text-sm text-slate-400">No reminders found.</p>
                  ) : (
                    reminders.slice(0, 5).map((item, index) => (
                      <div key={String(item.id ?? index)} className="border-b border-slate-800 py-3 last:border-0">
                        <p className="font-medium">{String(item.title ?? "Reminder")}</p>
                        <p className="mt-1 text-xs text-slate-400">
                          {String(item.scheduled_at ?? "Date not available")}
                        </p>
                      </div>
                    ))
                  )}
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                  <h3 className="mb-4 text-lg font-semibold">Recent messages</h3>
                  {messages.length === 0 ? (
                    <p className="text-sm text-slate-400">No messages found.</p>
                  ) : (
                    messages.slice(0, 5).map((item, index) => (
                      <div key={String(item.id ?? index)} className="flex justify-between gap-3 border-b border-slate-800 py-3 last:border-0">
                        <span className="text-sm">{String(item.email ?? item.title ?? `Message ${index + 1}`)}</span>
                        <span className="text-xs text-blue-400">{String(item.status ?? "Unknown")}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </>
          )}

          {activeTab === "contacts" && (
            <div className="grid gap-6 xl:grid-cols-2">
              <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                <h3 className="mb-4 text-lg font-semibold">Add new contact</h3>
                <form onSubmit={createContact} className="space-y-4">
                  <input required value={contactName} onChange={(e) => setContactName(e.target.value)} placeholder="Full name" className="field" />
                  <input required type="email" value={contactEmail} onChange={(e) => setContactEmail(e.target.value)} placeholder="Email address" className="field" />
                  <input value={company} onChange={(e) => setCompany(e.target.value)} placeholder="Company (optional)" className="field" />
                  <button className="primary">Create contact</button>
                </form>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                <h3 className="mb-4 text-lg font-semibold">Contact list ({contacts.length})</h3>
                {contacts.map((item, index) => (
                  <div key={String(item.id ?? index)} className="border-b border-slate-800 py-3">
                    <p className="font-medium">{String(item.name ?? "Unnamed contact")}</p>
                    <p className="text-sm text-slate-400">{String(item.email ?? "")}</p>
                    <p className="text-xs text-slate-500">{String(item.company ?? "")}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "templates" && (
            <div className="grid gap-6 xl:grid-cols-2">
              <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                <h3 className="mb-4 text-lg font-semibold">Create email template</h3>
                <form onSubmit={createTemplate} className="space-y-4">
                  <input required value={templateName} onChange={(e) => setTemplateName(e.target.value)} placeholder="Template name" className="field" />
                  <input required value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Email subject" className="field" />
                  <textarea required rows={7} value={html} onChange={(e) => setHtml(e.target.value)} placeholder="HTML email content" className="field" />
                  <p className="text-xs text-slate-400">You can use {"{{ name }}"} as a contact placeholder.</p>
                  <button className="primary">Save template</button>
                </form>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                <h3 className="mb-4 text-lg font-semibold">Saved templates ({templates.length})</h3>
                {templates.map((item, index) => (
                  <div key={String(item.id ?? index)} className="border-b border-slate-800 py-3">
                    <p className="font-medium">{String(item.name ?? "Template")}</p>
                    <p className="text-sm text-slate-400">{String(item.subject ?? "")}</p>
                    <p className="text-xs text-slate-500">ID: {String(item.id ?? "—")}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "campaigns" && (
            <div className="grid gap-6 xl:grid-cols-2">
              <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                <h3 className="mb-4 text-lg font-semibold">Create campaign</h3>
                <form onSubmit={createCampaign} className="space-y-4">
                  <input required value={campaignName} onChange={(e) => setCampaignName(e.target.value)} placeholder="Campaign name" className="field" />
                  <select required value={campaignTemplateId} onChange={(e) => setCampaignTemplateId(e.target.value)} className="field">
                    <option value="">Select an email template</option>
                    {templates.map((item, index) => (
                      <option key={String(item.id ?? index)} value={String(item.id ?? "")}>
                        {String(item.name ?? `Template ${index + 1}`)}
                      </option>
                    ))}
                  </select>
                  <button className="primary">Create campaign</button>
                </form>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                <h3 className="mb-4 text-lg font-semibold">Campaign list</h3>
                {campaigns.map((item, index) => (
                  <div key={String(item.id ?? index)} className="border-b border-slate-800 py-3">
                    <p className="font-medium">{String(item.name ?? "Campaign")}</p>
                    <p className="mb-2 text-xs text-slate-400">Status: {String(item.status ?? "Created")}</p>
                    <button onClick={() => sendCampaign(item.id)} className="rounded-lg bg-blue-600 px-3 py-2 text-xs hover:bg-blue-500">
                      Send campaign
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "reminders" && (
            <div className="grid gap-6 xl:grid-cols-2">
              <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                <h3 className="mb-4 text-lg font-semibold">Schedule a reminder</h3>
                <form onSubmit={createReminder} className="space-y-4">
                  <input required value={reminderTitle} onChange={(e) => setReminderTitle(e.target.value)} placeholder="Reminder title" className="field" />

                  <select required value={contactId} onChange={(e) => setContactId(e.target.value)} className="field">
                    <option value="">Select contact</option>
                    {contacts.map((item, index) => (
                      <option key={String(item.id ?? index)} value={String(item.id ?? "")}>
                        {String(item.name ?? item.email ?? `Contact ${index + 1}`)}
                      </option>
                    ))}
                  </select>

                  <select required value={templateId} onChange={(e) => setTemplateId(e.target.value)} className="field">
                    <option value="">Select template</option>
                    {templates.map((item, index) => (
                      <option key={String(item.id ?? index)} value={String(item.id ?? "")}>
                        {String(item.name ?? `Template ${index + 1}`)}
                      </option>
                    ))}
                  </select>

                  <label className="block text-sm text-slate-400">Scheduled date and time</label>
                  <input required type="datetime-local" value={scheduled} onChange={(e) => setScheduled(e.target.value)} className="field" />

                  <button className="primary">Schedule reminder</button>
                </form>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                <h3 className="mb-4 text-lg font-semibold">Scheduled reminders</h3>
                {reminders.map((item, index) => (
                  <div key={String(item.id ?? index)} className="border-b border-slate-800 py-3">
                    <p className="font-medium">{String(item.title ?? "Reminder")}</p>
                    <p className="text-xs text-slate-400">{String(item.scheduled_at ?? "")}</p>
                    <p className="text-xs text-blue-400">{String(item.status ?? "Scheduled")}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "messages" && (
            <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900 p-5">
              <h3 className="mb-4 text-lg font-semibold">Message activity</h3>
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-700 text-slate-400">
                    <th className="p-3">Recipient</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Message ID</th>
                  </tr>
                </thead>
                <tbody>
                  {messages.map((item, index) => (
                    <tr key={String(item.id ?? index)} className="border-b border-slate-800">
                      <td className="p-3">{String(item.email ?? item.title ?? "—")}</td>
                      <td className="p-3">{String(item.status ?? "Unknown")}</td>
                      <td className="p-3">{String(item.id ?? "—")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {messages.length === 0 && (
                <p className="py-5 text-sm text-slate-400">No messages available yet.</p>
              )}
            </div>
          )}

          {loading && (
            <p className="mt-5 text-sm text-slate-400">Loading dashboard data...</p>
          )}

          <footer className="mt-10 border-t border-slate-800 pt-5 text-xs text-slate-500">
            Email Automation & Reminder System · Development Dashboard
          </footer>
        </section>
      </div>

      <style jsx global>{`
        .field {
          width: 100%;
          border: 1px solid #334155;
          border-radius: 8px;
          background: #0f172a;
          color: white;
          padding: 11px 13px;
          outline: none;
        }
        .field:focus {
          border-color: #3b82f6;
        }
        .field::placeholder {
          color: #94a3b8;
        }
        .primary {
          width: 100%;
          border-radius: 8px;
          background: #2563eb;
          padding: 11px 15px;
          color: white;
          font-weight: 600;
        }
        .primary:hover {
          background: #1d4ed8;
        }
      `}</style>
    </main>
  );
}
